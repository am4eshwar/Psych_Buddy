"""Initialize models package"""
# Pydantic domain models (API / in-memory use)
from .user import UserProfile, UserSession
from .task import WellnessTask, CheckInPrompt, TaskType, TaskStatus, TaskPriority

# SQLAlchemy ORM models (PostgreSQL persistence)
from .db_models import (
    UserProfileDB,
    UserSessionDB,
    WellnessTaskDB,
    CheckInPromptDB,
)

__all__ = [
    # Pydantic
    'UserProfile',
    'UserSession',
    'WellnessTask',
    'CheckInPrompt',
    'TaskType',
    'TaskStatus',
    'TaskPriority',
    # SQLAlchemy
    'UserProfileDB',
    'UserSessionDB',
    'WellnessTaskDB',
    'CheckInPromptDB',
]
