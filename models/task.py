"""
Task data model
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum


class TaskType(str, Enum):
    """Types of wellness tasks"""
    BREATHING_EXERCISE = "breathing_exercise"
    PHYSICAL_ACTIVITY = "physical_activity"
    SOCIAL_CONNECTION = "social_connection"
    CREATIVE_EXPRESSION = "creative_expression"
    MINDFULNESS = "mindfulness"
    SELF_CARE = "self_care"
    JOURNALING = "journaling"
    RELAXATION = "relaxation"
    GOAL_SETTING = "goal_setting"
    CHECK_IN = "check_in"


class TaskPriority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    """Task completion status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class WellnessTask(BaseModel):
    """Individual wellness task"""
    task_id: str
    session_id: str
    user_id: str
    
    # Task details
    task_type: TaskType
    title: str
    description: str
    instructions: str
    
    # Scheduling
    scheduled_time: datetime
    duration_minutes: int = 15
    
    # Priority and status
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    
    # Calendar integration
    calendar_event_id: Optional[str] = None
    reminder_sent: bool = False
    
    # Completion tracking
    completed_at: Optional[datetime] = None
    user_feedback: Optional[str] = None
    effectiveness_rating: Optional[int] = None  # 1-5 scale
    
    # Additional metadata
    metadata: Dict[str, Any] = {}
    


class CheckInPrompt(BaseModel):
    """Check-in conversation prompt"""
    check_in_id: str
    session_id: str
    user_id: str
    
    # Timing
    scheduled_time: datetime
    completed_at: Optional[datetime] = None
    
    # Check-in content
    questions: list[str]
    user_responses: Dict[str, str] = {}
    
    # Mood tracking
    mood_score: Optional[int] = None  # 1-10 scale
    energy_level: Optional[int] = None  # 1-10 scale
    stress_level: Optional[int] = None  # 1-10 scale
    
    # AI analysis
    ai_insights: Optional[str] = None
    recommended_adjustments: list[str] = []
    
    status: TaskStatus = TaskStatus.PENDING
    
