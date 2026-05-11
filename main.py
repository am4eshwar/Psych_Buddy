"""
Psych Buddy - Multi-Agent System
Orchestrates Analysis Agent and Messaging Agent
Telegram-only communication platform

Memory Architecture:
  • Redis       — short-term session context
  • Mem0/Qdrant — episodic & semantic long-term memory
  • PostgreSQL  — task & schedule persistence
"""
import sys
import asyncio
import argparse
from loguru import logger

from config import (
    validate_config,
    LOG_LEVEL,
    LOGS_DIR,
    PROGRAM_DURATION_DAYS,
)
from core.memory import MemoryManager
from core.scheduler import WellnessScheduler
from core.agents import AgentOrchestrator
from mcp import (
    TelegramMCPServer,
    GoogleCalendarMCPServer,
    SpotifyMCPServer,
)


# ─── Logging ────────────────────────────────────────────────────
logger.remove()
logger.add(
    sys.stderr,
    level=LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
)
logger.add(
    LOGS_DIR / "psych_buddy_{time}.log",
    rotation="1 day",
    retention="7 days",
    level=LOG_LEVEL,
)


class MentalWellnessApp:
    """
    Psych Buddy Multi-Agent Application

    Architecture:
    - Analysis Agent: Emotional analysis, wellness planning, resource coordination
    - Messaging Agent: Communication, check-ins, crisis detection
    - Orchestrator: Coordinates agent collaboration
    - MemoryManager: Redis + Mem0/Qdrant + PostgreSQL
    """

    def __init__(self):
        """Initialize the Psych Buddy Multi-Agent Application"""
        logger.info("=" * 70)
        logger.info("Initializing Psych Buddy Multi-Agent System")
        logger.info("=" * 70)

        # Validate configuration
        try:
            validate_config()
            logger.info("✓ Configuration validated")
        except ValueError as e:
            logger.error(f"✗ Configuration validation failed: {e}")
            raise

        # Memory manager (async — initialized in start())
        self.memory = MemoryManager()

        # ── MCP Servers ──────────────────────────────────────────
        logger.info("Initializing MCP Servers...")

        # Telegram (required)
        try:
            self.telegram_server = TelegramMCPServer()
            logger.info("✓ Telegram server initialized")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Telegram: {e}")
            raise

        # Google Calendar (optional)
        self.calendar_server = None
        try:
            self.calendar_server = GoogleCalendarMCPServer()
            logger.info("✓ Google Calendar server initialized")
        except Exception as e:
            logger.warning(f"⚠ Google Calendar not available: {e}")

        # Spotify (optional)
        self.spotify_server = None
        try:
            self.spotify_server = SpotifyMCPServer()
            logger.info("✓ Spotify server initialized")
        except Exception as e:
            logger.warning(f"⚠ Spotify not available: {e}")

        # ── Agent Orchestrator ───────────────────────────────────
        logger.info("Initializing Multi-Agent Orchestrator...")
        self.orchestrator = AgentOrchestrator(
            memory_manager=self.memory,
            telegram_server=self.telegram_server,
            calendar_server=self.calendar_server,
            spotify_server=self.spotify_server,
        )
        logger.info("✓ Agent orchestrator initialized")
        logger.info("  → Analysis Agent: Ready (Gemini 2.0 Flash Thinking)")
        logger.info("  → Messaging Agent: Ready (Gemini 2.0 Flash)")

        # ── Scheduler ────────────────────────────────────────────
        logger.info("Initializing wellness scheduler...")
        self.scheduler = WellnessScheduler(self.memory)
        self.scheduler.register_check_in_callback("default", self.handle_check_in)
        self.scheduler.register_task_callback("default", self.handle_task_reminder)
        logger.info("✓ Scheduler initialized")

        # Register Telegram message handler
        self.telegram_server.register_message_handler(self.handle_user_message)

        logger.info("=" * 70)
        logger.info("Psych Buddy Multi-Agent System Ready!")
        logger.info("=" * 70)

    # ================================================================
    # Message Handling
    # ================================================================
    async def handle_user_message(self, user_id: str, message: str) -> str:
        """
        Handle incoming message from user via Telegram.

        Flow:
        1. Load context from Redis + Mem0 + PostgreSQL
        2. Route to orchestrator (new user vs existing session)
        3. Save turn back to Redis (+ periodic Mem0 consolidation)
        """
        logger.info(f"📨 Message received from user {user_id}")
        logger.debug(f"Message content: {message[:100]}...")

        try:
            # ── 1. Fetch unified context ─────────────────────────
            context = await self.memory.get_context_for_turn(user_id, message)
            logger.debug(
                f"Context loaded — {len(context['memories'])} memories, "
                f"{len(context['tasks'])} tasks, "
                f"{context['turn_count']} turns"
            )

            # ── 2. Save the user turn to Redis ───────────────────
            active_session = await self.memory.get_active_session(user_id)
            session_id = active_session.session_id if active_session else None
            await self.memory.save_turn(user_id, "user", message, session_id)

            # ── 3. Route to orchestrator ─────────────────────────
            if not active_session:
                logger.info("→ New user detected — Starting multi-agent onboarding")
                result = await self.orchestrator.handle_new_user_input(
                    user_id, message
                )

                # Schedule check-ins for new session
                if not result.get("is_crisis"):
                    self.scheduler.schedule_daily_check_ins(result["session"])
                    logger.info(
                        f"✓ Scheduled {PROGRAM_DURATION_DAYS * 4} check-ins"
                    )

                response = result["message"]
            else:
                logger.info("→ Existing user — Processing response")
                response = await self.orchestrator.handle_user_response(
                    user_id, message
                )

            # ── 4. Save the assistant turn to Redis ──────────────
            await self.memory.save_turn(
                user_id, "assistant", response, session_id
            )

            return response

        except Exception as e:
            logger.error(f"✗ Error handling user message: {e}", exc_info=True)
            return (
                "I apologize, but I encountered an error. "
                "Please try again or type /start to begin a new session."
            )

    async def handle_check_in(
        self, session_id: str, time_of_day: str, day_number: int
    ):
        """Handle scheduled check-in — delegates to orchestrator."""
        logger.info(
            f"⏰ Check-in triggered: Session {session_id}, "
            f"Day {day_number}, {time_of_day}"
        )
        try:
            await self.orchestrator.handle_check_in(
                session_id, time_of_day, day_number
            )
            logger.info("✓ Check-in completed successfully")
        except Exception as e:
            logger.error(f"✗ Error in check-in: {e}", exc_info=True)

    async def handle_task_reminder(self, task_id: str, session_id: str):
        """Handle task reminder — delegates to orchestrator."""
        logger.info(f"📋 Task reminder triggered: {task_id}")
        try:
            await self.orchestrator.handle_task_reminder(task_id, session_id)
            logger.info("✓ Task reminder sent successfully")
        except Exception as e:
            logger.error(f"✗ Error sending task reminder: {e}", exc_info=True)

    # ================================================================
    # Lifecycle
    # ================================================================
    async def start(self):
        """Start the multi-agent application (async)."""
        logger.info("=" * 70)
        logger.info("🚀 Starting Psych Buddy Multi-Agent System")
        logger.info("=" * 70)

        # ── Initialize memory (Redis + Mem0/Qdrant + PostgreSQL) ─
        await self.memory.initialize()
        logger.info("✓ Memory architecture online")

        # ── Start scheduler ──────────────────────────────────────
        logger.info("Starting wellness scheduler...")
        self.scheduler.start()
        logger.info("✓ Scheduler running")

        logger.info("=" * 70)
        logger.info("✅ System is now ACTIVE and monitoring for users")
        logger.info("=" * 70)
        logger.info("")
        logger.info("Active Components:")
        logger.info("  • Analysis Agent (Gemini 2.0 Flash Thinking)")
        logger.info("  • Messaging Agent (Gemini 2.0 Flash)")
        logger.info("  • Telegram Bot")
        logger.info(
            f"  • Google Calendar: {'✓' if self.calendar_server else '✗'}"
        )
        logger.info(f"  • Spotify: {'✓' if self.spotify_server else '✗'}")
        logger.info("  • Memory: Redis + Mem0/Qdrant + PostgreSQL")
        logger.info("  • Task Scheduler")
        logger.info("")
        logger.info("Press Ctrl+C to stop the system")
        logger.info("=" * 70)

        # ── Start Telegram bot ───────────────────────────────────
        logger.info("Starting Telegram bot...")
        await self.telegram_server.start_async()
        logger.info("✓ Telegram bot running")

    async def shutdown(self):
        """Gracefully shutdown all components and connections."""
        logger.info("=" * 70)
        logger.info("🛑 Shutting down Psych Buddy Multi-Agent System")
        logger.info("=" * 70)

        try:
            # Stop scheduler
            logger.info("Stopping scheduler...")
            self.scheduler.stop()
            logger.info("✓ Scheduler stopped")

            # Stop Telegram bot
            logger.info("Stopping Telegram bot...")
            await self.telegram_server.stop()
            logger.info("✓ Telegram bot stopped")

            # Close memory connections (Redis, PostgreSQL)
            logger.info("Closing memory connections...")
            await self.memory.close()
            logger.info("✓ Memory connections closed")

            logger.info("=" * 70)
            logger.info("✅ System shutdown complete")
            logger.info("=" * 70)

        except Exception as e:
            logger.error(f"✗ Error during shutdown: {e}", exc_info=True)


# ════════════════════════════════════════════════════════════════
# Entry Point
# ════════════════════════════════════════════════════════════════
async def async_main():
    """Async entry point."""
    app = MentalWellnessApp()
    try:
        await app.start()

        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("\n⚠ Keyboard interrupt received")
    except Exception as e:
        logger.error(f"✗ Critical application error: {e}", exc_info=True)
    finally:
        await app.shutdown()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Psych Buddy Multi-Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Multi-Agent Architecture:
  • Analysis Agent: Emotional analysis, wellness planning, resource coordination
  • Messaging Agent: Communication, check-ins, crisis detection

Communication: Telegram only
Memory: Redis (session) + Mem0/Qdrant (semantic) + PostgreSQL (tasks)
        """,
    )
    parser.parse_args()

    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"✗ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
