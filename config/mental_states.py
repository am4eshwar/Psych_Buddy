"""
Configuration settings for Psych Buddy
"""
from enum import Enum
from typing import List, Dict
from pydantic import BaseModel


class MentalState(str, Enum):
    """Primary mental states the agent can address"""
    SADNESS = "sadness"
    ANGER = "anger"
    ANXIETY = "anxiety"
    LONELINESS = "loneliness"
    GRIEF = "grief"
    STRESS = "stress"
    DEPRESSION = "depression"
    OVERWHELM = "overwhelm"
    FEAR = "fear"
    HOPELESSNESS = "hopelessness"


class IntensityLevel(str, Enum):
    """Intensity levels for mental states"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


class MentalStateProfile(BaseModel):
    """Profile for a specific mental state with metadata"""
    state: MentalState
    intensity: IntensityLevel
    duration_days: int = 7
    check_ins_per_day: int = 4
    
    # Associated emotions and symptoms
    related_emotions: List[str] = []
    
    # Risk factors
    requires_immediate_attention: bool = False
    professional_help_recommended: bool = False


# Mental state configurations
MENTAL_STATE_CONFIGS: Dict[MentalState, Dict] = {
    MentalState.SADNESS: {
        "description": "Feelings of unhappiness, sorrow, or dejection",
        "common_triggers": ["loss", "disappointment", "rejection", "isolation"],
        "intensity_indicators": {
            IntensityLevel.LOW: "Temporary sadness, able to function normally",
            IntensityLevel.MODERATE: "Persistent sadness affecting daily activities",
            IntensityLevel.HIGH: "Deep sadness with reduced motivation",
            IntensityLevel.SEVERE: "Severe sadness with inability to enjoy anything"
        },
        "typical_duration": 7,
        "professional_threshold": IntensityLevel.SEVERE
    },
    
    MentalState.LONELINESS: {
        "description": "Feeling of isolation or lack of connection",
        "common_triggers": ["social isolation", "breakup", "relocation", "loss"],
        "intensity_indicators": {
            IntensityLevel.LOW: "Occasional feelings of being alone",
            IntensityLevel.MODERATE: "Frequent loneliness affecting mood",
            IntensityLevel.HIGH: "Persistent loneliness causing distress",
            IntensityLevel.SEVERE: "Extreme isolation with hopelessness"
        },
        "typical_duration": 7,
        "professional_threshold": IntensityLevel.HIGH
    },
    
    MentalState.ANGER: {
        "description": "Strong feelings of displeasure or hostility",
        "common_triggers": ["injustice", "frustration", "betrayal", "loss of control"],
        "intensity_indicators": {
            IntensityLevel.LOW: "Mild irritation or annoyance",
            IntensityLevel.MODERATE: "Frequent anger affecting relationships",
            IntensityLevel.HIGH: "Intense anger with difficulty controlling",
            IntensityLevel.SEVERE: "Rage with potential for harm"
        },
        "typical_duration": 7,
        "professional_threshold": IntensityLevel.SEVERE
    },
    
    MentalState.ANXIETY: {
        "description": "Persistent worry, nervousness, or unease",
        "common_triggers": ["uncertainty", "stress", "trauma", "change"],
        "intensity_indicators": {
            IntensityLevel.LOW: "Occasional worry about specific things",
            IntensityLevel.MODERATE: "Regular anxiety affecting daily life",
            IntensityLevel.HIGH: "Severe anxiety with physical symptoms",
            IntensityLevel.SEVERE: "Panic attacks, unable to function"
        },
        "typical_duration": 7,
        "professional_threshold": IntensityLevel.HIGH
    },
    
    MentalState.GRIEF: {
        "description": "Deep sorrow from loss or bereavement",
        "common_triggers": ["death", "breakup", "loss of relationship", "major change"],
        "intensity_indicators": {
            IntensityLevel.LOW: "Accepting the loss, occasional sadness",
            IntensityLevel.MODERATE: "Processing grief, emotional fluctuations",
            IntensityLevel.HIGH: "Deep grief affecting functioning",
            IntensityLevel.SEVERE: "Complicated grief, unable to accept loss"
        },
        "typical_duration": 14,  # Grief often needs longer
        "professional_threshold": IntensityLevel.SEVERE
    },
    
    MentalState.STRESS: {
        "description": "Mental or emotional strain from demanding circumstances",
        "common_triggers": ["work pressure", "deadlines", "responsibilities", "conflicts"],
        "intensity_indicators": {
            IntensityLevel.LOW: "Manageable stress, productive pressure",
            IntensityLevel.MODERATE: "Regular stress affecting sleep or mood",
            IntensityLevel.HIGH: "Chronic stress with burnout symptoms",
            IntensityLevel.SEVERE: "Extreme stress, breakdown imminent"
        },
        "typical_duration": 7,
        "professional_threshold": IntensityLevel.SEVERE
    },
    
    MentalState.DEPRESSION: {
        "description": "Persistent low mood and loss of interest",
        "common_triggers": ["trauma", "loss", "chronic stress", "biochemical factors"],
        "intensity_indicators": {
            IntensityLevel.LOW: "Mild depressive symptoms",
            IntensityLevel.MODERATE: "Moderate depression affecting daily life",
            IntensityLevel.HIGH: "Severe depression, significant impairment",
            IntensityLevel.SEVERE: "Critical depression, potential self-harm risk"
        },
        "typical_duration": 14,
        "professional_threshold": IntensityLevel.MODERATE,
        "requires_professional": True
    },
    
    MentalState.OVERWHELM: {
        "description": "Feeling unable to cope with demands",
        "common_triggers": ["too many responsibilities", "major changes", "lack of support"],
        "intensity_indicators": {
            IntensityLevel.LOW: "Temporarily overwhelmed, can recover",
            IntensityLevel.MODERATE: "Frequently overwhelmed, reduced capacity",
            IntensityLevel.HIGH: "Constantly overwhelmed, shutting down",
            IntensityLevel.SEVERE: "Complete overwhelm, unable to function"
        },
        "typical_duration": 7,
        "professional_threshold": IntensityLevel.HIGH
    },
    
    MentalState.FEAR: {
        "description": "Intense emotion in response to perceived threat",
        "common_triggers": ["trauma", "phobia", "uncertainty", "danger"],
        "intensity_indicators": {
            IntensityLevel.LOW: "Mild fear about specific situations",
            IntensityLevel.MODERATE: "Regular fear limiting activities",
            IntensityLevel.HIGH: "Severe fear with avoidance behavior",
            IntensityLevel.SEVERE: "Paralyzing fear, panic responses"
        },
        "typical_duration": 7,
        "professional_threshold": IntensityLevel.HIGH
    },
    
    MentalState.HOPELESSNESS: {
        "description": "Feeling that things will not improve",
        "common_triggers": ["chronic problems", "repeated failures", "trauma", "depression"],
        "intensity_indicators": {
            IntensityLevel.LOW: "Occasional pessimism",
            IntensityLevel.MODERATE: "Frequent hopelessness about future",
            IntensityLevel.HIGH: "Deep hopelessness, giving up",
            IntensityLevel.SEVERE: "Complete hopelessness, suicidal ideation"
        },
        "typical_duration": 14,
        "professional_threshold": IntensityLevel.MODERATE,
        "requires_professional": True,
        "crisis_risk": True
    }
}


# Crisis keywords that trigger immediate professional help recommendations
CRISIS_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "end my life", "not worth living",
    "self-harm", "hurt myself", "cutting", "overdose", "die", "death wish"
]


# Emergency resources
EMERGENCY_RESOURCES = {
    "US": {
        "crisis_line": "988 (Suicide & Crisis Lifeline)",
        "crisis_text": "Text HOME to 741741",
        "emergency": "911"
    },
    "International": {
        "resource": "https://findahelpline.com",
        "description": "Find local crisis helplines worldwide"
    }
}
