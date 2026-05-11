"""
User data model
"""
from datetime import datetime, timezone
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from config.mental_states import MentalState, IntensityLevel


class UserProfile(BaseModel):
    """User profile information"""
    user_id: str
    age: Optional[int] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    telegram_id: Optional[str] = None
    preferred_contact: str = "telegram"  # telegram or whatsapp
    timezone: str = "UTC"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    

class UserSession(BaseModel):
    """Active wellness session for a user"""
    session_id: str
    user_id: str
    
    # Mental state information
    primary_mental_state: MentalState
    secondary_mental_states: List[MentalState] = []
    intensity: IntensityLevel
    
    # Context and trigger
    trigger_event: str
    context: str
    initial_prompt: str
    
    # Session metadata
    start_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_date: Optional[datetime] = None
    duration_days: int = 7
    
    # AI-generated plan
    wellness_plan: Optional[Dict] = None
    coping_strategies: List[str] = []
    
    # Progress tracking
    completed_check_ins: int = 0
    total_check_ins: int = 28  # 4 per day * 7 days
    completed_tasks: List[str] = []
    mood_scores: List[int] = []  # Daily mood scores 1-10
    
    # Status
    is_active: bool = True
    requires_professional_help: bool = False
    

