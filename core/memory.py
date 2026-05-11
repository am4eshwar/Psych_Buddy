"""
Advanced Memory Manager
Orchestrates three storage layers:
  1. Redis       — Short-term session context (TTL-based)
  2. Mem0/Qdrant — Episodic & semantic memory (long-term)
  3. PostgreSQL  — Task & schedule persistence (structured)
"""
import asyncio
import json
import os
from datetime import datetime, timedelta, date, timezone
from typing import Optional, List, Dict, Any

import redis.asyncio as aioredis
from mem0 import Memory
from loguru import logger
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from config import (
    GOOGLE_API_KEY,
    REDIS_URL, REDIS_SESSION_TTL,
    MEM0_TOP_K, MEMORY_RETENTION_DAYS,
    CONSOLIDATION_INTERVAL_TURNS,
    get_mem0_config,
)
from core.database import async_session_factory, init_db, close_db
from models.db_models import (
    UserProfileDB, UserSessionDB, WellnessTaskDB, CheckInPromptDB,
)
from models import UserProfile, UserSession, WellnessTask, CheckInPrompt


class MemoryManager:
    """
    Unified memory manager.

    Usage:
        mgr = MemoryManager()
        await mgr.initialize()   # call once at startup
        ...
        await mgr.close()        # call on shutdown
    """

    def __init__(self):
        self._redis: Optional[aioredis.Redis] = None
        self._mem0: Optional[Memory] = None
        self._initialized = False

    # ================================================================
    # Lifecycle
    # ================================================================
    async def initialize(self):
        """Connect to Redis, Mem0/Qdrant, and PostgreSQL."""
        logger.info("Initializing Advanced Memory Manager...")

        # --- Redis ---
        try:
            self._redis = aioredis.from_url(
                REDIS_URL, decode_responses=True
            )
            await self._redis.ping()
            logger.info("  ✓ Redis connected")
        except Exception as e:
            logger.error(f"  ✗ Redis connection failed: {e}")
            self._redis = None

        # --- Mem0 + Qdrant ---
        try:
            # litellm reads GEMINI_API_KEY for google models
            os.environ["GEMINI_API_KEY"] = GOOGLE_API_KEY or ""
            config = get_mem0_config()
            self._mem0 = Memory.from_config(config)
            logger.info("  ✓ Mem0 + Qdrant initialized")
        except Exception as e:
            logger.error(f"  ✗ Mem0 initialization failed: {e}")
            self._mem0 = None

        # --- PostgreSQL ---
        try:
            await init_db()
            logger.info("  ✓ PostgreSQL ready")
        except Exception as e:
            logger.error(f"  ✗ PostgreSQL init failed: {e}")

        self._initialized = True
        logger.info("Advanced Memory Manager initialized")

    async def close(self):
        """Gracefully release all connections."""
        if self._redis:
            await self._redis.aclose()
            logger.info("  ✓ Redis closed")
        await close_db()
        logger.info("  ✓ PostgreSQL closed")

    # ================================================================
    # 1. REDIS — Session Context (short-term)
    # ================================================================
    async def load_session_context(self, user_id: str) -> Dict[str, Any]:
        """Load session context from Redis. Returns empty dict on miss."""
        if not self._redis:
            return {}
        try:
            raw = await self._redis.get(f"session:{user_id}")
            return json.loads(raw) if raw else {}
        except Exception as e:
            logger.warning(f"Redis load failed for {user_id}: {e}")
            return {}

    async def save_session_context(
        self, user_id: str, context: Dict[str, Any]
    ):
        """Write session context back to Redis with TTL."""
        if not self._redis:
            return
        try:
            await self._redis.set(
                f"session:{user_id}",
                json.dumps(context, default=str),
                ex=REDIS_SESSION_TTL,
            )
        except Exception as e:
            logger.warning(f"Redis save failed for {user_id}: {e}")

    async def clear_session_context(self, user_id: str):
        """Delete session context from Redis."""
        if not self._redis:
            return
        try:
            await self._redis.delete(f"session:{user_id}")
        except Exception as e:
            logger.warning(f"Redis clear failed for {user_id}: {e}")

    async def get_conversation_history(self, session_identifier: str, limit: int = 15) -> List[Dict[str, str]]:
        """
        Get recent conversation history.
        Accepts user_id or session_id (will fallback to user_id lookup).
        """
        # Our redis keys are currently based on user_id, but agents might pass session_id.
        # If it's a UUID/session_id we should ideally have a secondary index, but for now 
        # let's assume it might be either. Usually it's passed user_id in our latest refactors.
        # Actually, let's just fetch it. 
        # If it fails, return empty.
        ctx = await self.load_session_context(session_identifier)
        messages = ctx.get("messages", [])
        return messages[-limit:]

    # ================================================================
    # 2. MEM0 / QDRANT — Episodic & Semantic Memory (long-term)
    # ================================================================
    async def retrieve_memories(
        self, user_id: str, query: str, top_k: int = MEM0_TOP_K
    ) -> List[Dict[str, Any]]:
        """Semantic search against Qdrant via Mem0."""
        if not self._mem0:
            return []
        try:
            results = await asyncio.to_thread(
                self._mem0.search, query, filters={"user_id": user_id}, limit=top_k
            )
            return results.get("results", []) if isinstance(results, dict) else results
        except Exception as e:
            logger.error(f"Mem0 search failed: {e}")
            return []

    async def add_memory(
        self, user_id: str, text: str, metadata: Optional[Dict] = None
    ):
        """Store a single memory entry via Mem0."""
        if not self._mem0:
            return
        try:
            await asyncio.to_thread(
                self._mem0.add, text, user_id=user_id, metadata=metadata or {}
            )
        except Exception as e:
            logger.error(f"Mem0 add failed: {e}")

    async def consolidate_session(self, user_id: str, messages: List[Dict]):
        """
        End-of-session consolidation:
        Extract facts from conversation, deduplicate, update Qdrant.
        """
        if not self._mem0 or not messages:
            return
        try:
            conversation_text = "\n".join(
                f"{m.get('role', 'user')}: {m.get('content', '')}"
                for m in messages
            )
            await asyncio.to_thread(
                self._mem0.add,
                conversation_text,
                user_id=user_id,
                metadata={"type": "session_consolidation",
                          "timestamp": datetime.now(timezone.utc).isoformat()},
            )
            logger.info(f"Session consolidated for user {user_id}")
        except Exception as e:
            logger.error(f"Mem0 consolidation failed: {e}")

    async def get_all_memories(self, user_id: str) -> List[Dict]:
        """Return all stored memories for a user."""
        if not self._mem0:
            return []
        try:
            results = await asyncio.to_thread(
                self._mem0.get_all, user_id=user_id
            )
            return results.get("results", []) if isinstance(results, dict) else results
        except Exception as e:
            logger.error(f"Mem0 get_all failed: {e}")
            return []

    # ================================================================
    # 3. POSTGRESQL — Structured Persistence
    # ================================================================

    # --- User Profiles ---
    async def save_user_profile(self, profile: UserProfile) -> bool:
        try:
            async with async_session_factory() as session:
                db_obj = await session.get(UserProfileDB, profile.user_id)
                data = profile.model_dump(exclude={"created_at"})
                for k, v in data.items():
                    if isinstance(v, datetime) and v.tzinfo:
                        data[k] = v.replace(tzinfo=None)
                if db_obj:
                    for k, v in data.items():
                        setattr(db_obj, k, v)
                else:
                    db_obj = UserProfileDB(**data)
                    session.add(db_obj)
                await session.commit()
            return True
        except Exception as e:
            logger.error(f"PG save profile failed: {e}")
            return False

    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        try:
            async with async_session_factory() as session:
                db_obj = await session.get(UserProfileDB, user_id)
                if not db_obj:
                    return None
                return UserProfile(
                    user_id=db_obj.user_id, age=db_obj.age,
                    gender=db_obj.gender, phone_number=db_obj.phone_number,
                    telegram_id=db_obj.telegram_id,
                    preferred_contact=db_obj.preferred_contact,
                    timezone=db_obj.timezone, created_at=db_obj.created_at,
                )
        except Exception as e:
            logger.error(f"PG get profile failed: {e}")
            return None

    # --- Sessions ---
    async def save_session(self, user_session: UserSession) -> bool:
        try:
            async with async_session_factory() as session:
                db_obj = await session.get(UserSessionDB, user_session.session_id)
                data = user_session.model_dump()
                for k, v in data.items():
                    if isinstance(v, datetime) and v.tzinfo:
                        data[k] = v.replace(tzinfo=None)
                # Convert enums to strings for JSON columns
                data["primary_mental_state"] = getattr(data["primary_mental_state"], "value", str(data["primary_mental_state"]))
                data["secondary_mental_states"] = [getattr(s, "value", str(s)) for s in data["secondary_mental_states"]]
                data["intensity"] = getattr(data["intensity"], "value", str(data["intensity"]))
                if db_obj:
                    for k, v in data.items():
                        if hasattr(db_obj, k):
                            setattr(db_obj, k, v)
                else:
                    db_obj = UserSessionDB(**data)
                    session.add(db_obj)
                await session.commit()
            return True
        except Exception as e:
            logger.error(f"PG save session failed: {e}")
            return False

    async def get_active_session(self, user_id: str) -> Optional[UserSession]:
        try:
            async with async_session_factory() as session:
                stmt = select(UserSessionDB).where(
                    and_(
                        UserSessionDB.user_id == user_id,
                        UserSessionDB.is_active == True,
                    )
                )
                result = await session.execute(stmt)
                db_obj = result.scalar_one_or_none()
                if not db_obj:
                    return None
                return self._session_db_to_pydantic(db_obj)
        except Exception as e:
            logger.error(f"PG get active session failed: {e}")
            return None

    async def get_user_sessions(self, user_id: str) -> List[UserSession]:
        try:
            async with async_session_factory() as session:
                stmt = select(UserSessionDB).where(
                    UserSessionDB.user_id == user_id
                )
                result = await session.execute(stmt)
                return [self._session_db_to_pydantic(r) for r in result.scalars().all()]
        except Exception as e:
            logger.error(f"PG get sessions failed: {e}")
            return []

    async def update_session_progress(
        self, session_id: str, mood_scores: List[int], completed_tasks: List[str]
    ) -> bool:
        try:
            async with async_session_factory() as session:
                db_obj = await session.get(UserSessionDB, session_id)
                if not db_obj:
                    return False
                db_obj.mood_scores = mood_scores
                db_obj.completed_tasks = completed_tasks
                await session.commit()
            return True
        except Exception as e:
            logger.error(f"PG update progress failed: {e}")
            return False

    async def deactivate_session(self, session_id: str) -> bool:
        try:
            async with async_session_factory() as session:
                db_obj = await session.get(UserSessionDB, session_id)
                if not db_obj:
                    return False
                db_obj.is_active = False
                db_obj.end_date = datetime.now(timezone.utc)
                await session.commit()
            return True
        except Exception as e:
            logger.error(f"PG deactivate session failed: {e}")
            return False

    # --- Tasks ---
    async def save_task(self, task: WellnessTask) -> bool:
        try:
            async with async_session_factory() as session:
                db_obj = await session.get(WellnessTaskDB, task.task_id)
                data = task.model_dump()
                for k, v in data.items():
                    if isinstance(v, datetime) and v.tzinfo:
                        data[k] = v.replace(tzinfo=None)
                data["task_type"] = getattr(data["task_type"], "value", str(data["task_type"]))
                data["priority"] = getattr(data["priority"], "value", str(data["priority"]))
                data["status"] = getattr(data["status"], "value", str(data["status"]))
                data["metadata_json"] = data.pop("metadata", {})
                if db_obj:
                    for k, v in data.items():
                        if hasattr(db_obj, k):
                            setattr(db_obj, k, v)
                else:
                    db_obj = WellnessTaskDB(**data)
                    session.add(db_obj)
                await session.commit()
            return True
        except Exception as e:
            logger.error(f"PG save task failed: {e}")
            return False

    async def get_todays_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """Get today's tasks + any overdue items for the user."""
        try:
            today_start = datetime.combine(date.today(), datetime.min.time())
            today_end = today_start + timedelta(days=1)
            async with async_session_factory() as session:
                stmt = select(WellnessTaskDB).where(
                    and_(
                        WellnessTaskDB.user_id == user_id,
                        or_(
                            # Today's tasks
                            and_(
                                WellnessTaskDB.scheduled_time >= today_start,
                                WellnessTaskDB.scheduled_time < today_end,
                            ),
                            # Overdue (past + still pending)
                            and_(
                                WellnessTaskDB.scheduled_time < today_start,
                                WellnessTaskDB.status == "pending",
                            ),
                        ),
                    )
                ).order_by(WellnessTaskDB.scheduled_time)
                result = await session.execute(stmt)
                tasks = []
                for t in result.scalars().all():
                    tasks.append({
                        "task_id": t.task_id,
                        "title": t.title,
                        "description": t.description,
                        "task_type": t.task_type,
                        "scheduled_time": t.scheduled_time.isoformat(),
                        "status": t.status,
                        "priority": t.priority,
                        "overdue": t.scheduled_time < today_start,
                    })
                return tasks
        except Exception as e:
            logger.error(f"PG get today's tasks failed: {e}")
            return []

    async def update_task_status(
        self, task_id: str, status: str, user_id: Optional[str] = None
    ) -> bool:
        """Update task status. Optionally triggers a Mem0 episodic update."""
        try:
            async with async_session_factory() as session:
                db_obj = await session.get(WellnessTaskDB, task_id)
                if not db_obj:
                    return False
                db_obj.status = status
                if status == "completed":
                    db_obj.completed_at = datetime.now(timezone.utc)
                await session.commit()

            # Episodic memory update for task state change
            uid = user_id or (db_obj.user_id if db_obj else None)
            if uid:
                await self.add_memory(
                    uid,
                    f"Task '{db_obj.title}' status changed to {status}",
                    metadata={"type": "task_update", "task_id": task_id},
                )
            return True
        except Exception as e:
            logger.error(f"PG update task status failed: {e}")
            return False

    # --- Check-ins ---
    async def save_check_in(self, check_in: CheckInPrompt) -> bool:
        try:
            async with async_session_factory() as session:
                data = check_in.model_dump()
                for k, v in data.items():
                    if isinstance(v, datetime) and v.tzinfo:
                        data[k] = v.replace(tzinfo=None)
                data["status"] = getattr(data["status"], "value", str(data["status"]))
                db_obj = CheckInPromptDB(**data)
                session.add(db_obj)
                await session.commit()
            return True
        except Exception as e:
            logger.error(f"PG save check-in failed: {e}")
            return False

    # ================================================================
    # 4. UNIFIED CONTEXT — The main orchestration method
    # ================================================================
    async def get_context_for_turn(
        self, user_id: str, current_message: str = ""
    ) -> Dict[str, Any]:
        """
        Parallel-fetch from all three layers and merge into a
        structured context dict for system prompt injection.
        """
        query = current_message or f"user {user_id} current context"

        session_ctx, memories, tasks = await asyncio.gather(
            self.load_session_context(user_id),
            self.retrieve_memories(user_id, query),
            self.get_todays_tasks(user_id),
            return_exceptions=True,
        )

        # Normalise exceptions to empty defaults
        if isinstance(session_ctx, Exception):
            logger.warning(f"Context fetch (redis) error: {session_ctx}")
            session_ctx = {}
        if isinstance(memories, Exception):
            logger.warning(f"Context fetch (mem0) error: {memories}")
            memories = []
        if isinstance(tasks, Exception):
            logger.warning(f"Context fetch (pg) error: {tasks}")
            tasks = []

        return {
            "session_history": session_ctx.get("messages", []),
            "turn_count": session_ctx.get("turn_count", 0),
            "memories": memories,
            "tasks": tasks,
        }

    async def save_turn(
        self, user_id: str, role: str, content: str,
        session_id: Optional[str] = None,
    ):
        """
        After each message turn:
        1. Append to Redis session context
        2. Increment turn counter
        3. If N turns reached → trigger background consolidation
        """
        ctx = await self.load_session_context(user_id)
        messages = ctx.get("messages", [])
        turn_count = ctx.get("turn_count", 0) + (1 if role == "user" else 0)

        messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        ctx.update({
            "user_id": user_id,
            "session_id": session_id or ctx.get("session_id"),
            "messages": messages,
            "turn_count": turn_count,
        })
        await self.save_session_context(user_id, ctx)

        # Periodic consolidation
        if turn_count > 0 and turn_count % CONSOLIDATION_INTERVAL_TURNS == 0:
            logger.info(
                f"Turn {turn_count} — triggering background consolidation for {user_id}"
            )
            asyncio.create_task(self.consolidate_session(user_id, messages))

    # ================================================================
    # 5. Maintenance
    # ================================================================
    async def cleanup_old_data(self) -> bool:
        """Remove sessions and tasks older than MEMORY_RETENTION_DAYS."""
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=MEMORY_RETENTION_DAYS)
            async with async_session_factory() as session:
                # Delete old check-ins
                old_sessions_stmt = select(UserSessionDB.session_id).where(
                    UserSessionDB.end_date < cutoff
                )
                result = await session.execute(old_sessions_stmt)
                old_ids = [r[0] for r in result.all()]
                if old_ids:
                    for model in (CheckInPromptDB, WellnessTaskDB, UserSessionDB):
                        if model == UserSessionDB:
                            await session.execute(
                                model.__table__.delete().where(
                                    model.session_id.in_(old_ids)
                                )
                            )
                        else:
                            await session.execute(
                                model.__table__.delete().where(
                                    model.session_id.in_(old_ids)
                                )
                            )
                    await session.commit()
                    logger.info(f"Cleaned up {len(old_ids)} old sessions")
            return True
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False

    # ================================================================
    # Helpers
    # ================================================================
    @staticmethod
    def _session_db_to_pydantic(db_obj: UserSessionDB) -> UserSession:
        """Convert SQLAlchemy UserSessionDB → Pydantic UserSession."""
        return UserSession(
            session_id=db_obj.session_id,
            user_id=db_obj.user_id,
            primary_mental_state=db_obj.primary_mental_state,
            secondary_mental_states=db_obj.secondary_mental_states or [],
            intensity=db_obj.intensity,
            trigger_event=db_obj.trigger_event,
            context=db_obj.context,
            initial_prompt=db_obj.initial_prompt,
            start_date=db_obj.start_date,
            end_date=db_obj.end_date,
            duration_days=db_obj.duration_days,
            wellness_plan=db_obj.wellness_plan,
            coping_strategies=db_obj.coping_strategies or [],
            completed_check_ins=db_obj.completed_check_ins,
            total_check_ins=db_obj.total_check_ins,
            completed_tasks=db_obj.completed_tasks or [],
            mood_scores=db_obj.mood_scores or [],
            is_active=db_obj.is_active,
            requires_professional_help=db_obj.requires_professional_help,
        )