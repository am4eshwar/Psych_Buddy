"""
SQLAlchemy ORM Models for PostgreSQL

Maps the domain Pydantic models to relational tables.
Tables:
  - user_profiles   → UserProfile
  - user_sessions   → UserSession
  - wellness_tasks  → WellnessTask
  - check_in_prompts → CheckInPrompt
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    String, Integer, Boolean, DateTime, Text, JSON,
    ForeignKey, Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


# ═══════════════════════════════════════════════════════════════
# User Profile
# ═══════════════════════════════════════════════════════════════
class UserProfileDB(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    telegram_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    preferred_contact: Mapped[str] = mapped_column(String(16), default="telegram")
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    sessions = relationship("UserSessionDB", back_populates="user", lazy="selectin")

    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id})>"


# ═══════════════════════════════════════════════════════════════
# User Session
# ═══════════════════════════════════════════════════════════════
class UserSessionDB(Base):
    __tablename__ = "user_sessions"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("user_profiles.user_id"), index=True
    )

    # Mental state
    primary_mental_state: Mapped[str] = mapped_column(String(32))
    secondary_mental_states: Mapped[list] = mapped_column(JSON, default=list)
    intensity: Mapped[str] = mapped_column(String(16))

    # Context
    trigger_event: Mapped[str] = mapped_column(Text)
    context: Mapped[str] = mapped_column(Text)
    initial_prompt: Mapped[str] = mapped_column(Text)

    # Session metadata
    start_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_days: Mapped[int] = mapped_column(Integer, default=7)

    # AI-generated plan
    wellness_plan: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    coping_strategies: Mapped[list] = mapped_column(JSON, default=list)

    # Progress tracking
    completed_check_ins: Mapped[int] = mapped_column(Integer, default=0)
    total_check_ins: Mapped[int] = mapped_column(Integer, default=28)
    completed_tasks: Mapped[list] = mapped_column(JSON, default=list)
    mood_scores: Mapped[list] = mapped_column(JSON, default=list)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    requires_professional_help: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    user = relationship("UserProfileDB", back_populates="sessions")
    tasks = relationship("WellnessTaskDB", back_populates="session", lazy="selectin")
    check_ins = relationship("CheckInPromptDB", back_populates="session", lazy="selectin")

    # Indexes for common queries
    __table_args__ = (
        Index("ix_sessions_user_active", "user_id", "is_active"),
    )

    def __repr__(self):
        return f"<UserSession(session_id={self.session_id}, user_id={self.user_id}, active={self.is_active})>"


# ═══════════════════════════════════════════════════════════════
# Wellness Task
# ═══════════════════════════════════════════════════════════════
class WellnessTaskDB(Base):
    __tablename__ = "wellness_tasks"

    task_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("user_sessions.session_id"), index=True
    )
    user_id: Mapped[str] = mapped_column(String(64), index=True)

    # Task details
    task_type: Mapped[str] = mapped_column(String(32))
    title: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(Text)
    instructions: Mapped[str] = mapped_column(Text)

    # Scheduling
    scheduled_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=15)

    # Priority and status
    priority: Mapped[str] = mapped_column(String(16), default="medium")
    status: Mapped[str] = mapped_column(String(16), default="pending", index=True)

    # Calendar integration
    calendar_event_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)

    # Completion tracking
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    user_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    effectiveness_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Additional metadata
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    # Relationships
    session = relationship("UserSessionDB", back_populates="tasks")

    # Indexes for task retrieval queries
    __table_args__ = (
        Index("ix_tasks_user_status", "user_id", "status"),
        Index("ix_tasks_user_scheduled", "user_id", "scheduled_time"),
    )

    def __repr__(self):
        return f"<WellnessTask(task_id={self.task_id}, title={self.title}, status={self.status})>"


# ═══════════════════════════════════════════════════════════════
# Check-In Prompt
# ═══════════════════════════════════════════════════════════════
class CheckInPromptDB(Base):
    __tablename__ = "check_in_prompts"

    check_in_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("user_sessions.session_id"), index=True
    )
    user_id: Mapped[str] = mapped_column(String(64), index=True)

    # Timing
    scheduled_time: Mapped[datetime] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Check-in content
    questions: Mapped[list] = mapped_column(JSON, default=list)
    user_responses: Mapped[dict] = mapped_column(JSON, default=dict)

    # Mood tracking
    mood_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    energy_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    stress_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # AI analysis
    ai_insights: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommended_adjustments: Mapped[list] = mapped_column(JSON, default=list)

    status: Mapped[str] = mapped_column(String(16), default="pending")

    # Relationships
    session = relationship("UserSessionDB", back_populates="check_ins")

    def __repr__(self):
        return f"<CheckInPrompt(check_in_id={self.check_in_id}, status={self.status})>"
