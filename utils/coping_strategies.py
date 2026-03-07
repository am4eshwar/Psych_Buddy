"""
Coping strategies database organized by mental state
"""
from typing import Dict, List
from config.mental_states import MentalState


class CopingStrategiesDB:
    """Database of evidence-based coping strategies"""
    
    STRATEGIES: Dict[MentalState, Dict[str, List[str]]] = {
        MentalState.SADNESS: {
            "immediate": [
                "Practice deep breathing: 4-7-8 technique (breathe in for 4, hold for 7, out for 8)",
                "Listen to uplifting or comforting music",
                "Take a short walk outside, focus on nature",
                "Call or text a trusted friend",
                "Write down 3 things you're grateful for today"
            ],
            "daily_activities": [
                "Maintain a regular sleep schedule",
                "Exercise for at least 20 minutes",
                "Spend time in sunlight or bright light",
                "Engage in a hobby you enjoy",
                "Practice self-compassion meditation",
                "Limit social media usage",
                "Eat nutritious, regular meals"
            ],
            "social": [
                "Reach out to supportive friends or family",
                "Join a support group or online community",
                "Volunteer to help others",
                "Schedule regular social activities",
                "Share your feelings with someone you trust"
            ],
            "therapeutic": [
                "Journal about your emotions without judgment",
                "Practice cognitive reframing",
                "Use positive affirmations",
                "Try art or music therapy",
                "Consider talking to a therapist"
            ]
        },
        
        MentalState.LONELINESS: {
            "immediate": [
                "Call or video chat with someone you care about",
                "Join an online community with shared interests",
                "Go to a public place (coffee shop, library, park)",
                "Send a message to reconnect with an old friend",
                "Watch or listen to content that feels comforting"
            ],
            "daily_activities": [
                "Take a class or workshop to meet new people",
                "Adopt a pet or volunteer at animal shelter",
                "Join a club or group activity",
                "Establish a routine that includes social contact",
                "Practice self-companionship activities"
            ],
            "social": [
                "Use apps to find local meetups or events",
                "Reconnect with old friends",
                "Be a regular at a local spot (café, gym, bookstore)",
                "Join online communities or forums",
                "Volunteer in your community"
            ],
            "therapeutic": [
                "Practice self-compassion and self-acceptance",
                "Write letters to yourself",
                "Explore the difference between being alone and lonely",
                "Address negative self-talk",
                "Consider therapy for social anxiety if applicable"
            ]
        },
        
        MentalState.ANGER: {
            "immediate": [
                "Take 10 deep breaths before responding",
                "Go for a vigorous walk or run",
                "Punch a pillow or do physical exercise",
                "Count to 10 (or 100) slowly",
                "Step away from the situation temporarily"
            ],
            "daily_activities": [
                "Regular physical exercise for stress release",
                "Practice progressive muscle relaxation",
                "Maintain consistent sleep schedule",
                "Limit caffeine and alcohol",
                "Use a stress ball or fidget tool"
            ],
            "communication": [
                "Use 'I' statements to express feelings",
                "Practice active listening",
                "Take breaks during heated discussions",
                "Write down angry thoughts before speaking",
                "Learn assertiveness techniques"
            ],
            "therapeutic": [
                "Keep an anger journal to identify triggers",
                "Practice mindfulness meditation",
                "Learn anger management techniques",
                "Explore underlying emotions beneath anger",
                "Consider cognitive behavioral therapy"
            ]
        },
        
        MentalState.ANXIETY: {
            "immediate": [
                "Ground yourself with 5-4-3-2-1 technique",
                "Practice box breathing (4-4-4-4)",
                "Progressive muscle relaxation",
                "Splash cold water on your face",
                "Listen to calming music or nature sounds"
            ],
            "daily_activities": [
                "Limit caffeine intake",
                "Exercise regularly (yoga, walking, swimming)",
                "Maintain consistent sleep schedule",
                "Practice daily meditation or mindfulness",
                "Reduce screen time before bed",
                "Eat balanced, regular meals"
            ],
            "cognitive": [
                "Challenge anxious thoughts with evidence",
                "Practice thought-stopping techniques",
                "Use positive self-talk",
                "Keep a worry journal with scheduled worry time",
                "Distinguish between helpful and unhelpful worry"
            ],
            "therapeutic": [
                "Learn CBT techniques for anxiety",
                "Practice exposure therapy for specific fears",
                "Try guided meditation apps",
                "Consider therapy or counseling",
                "Explore medication options with a doctor if severe"
            ]
        },
        
        MentalState.GRIEF: {
            "immediate": [
                "Allow yourself to feel emotions without judgment",
                "Reach out to supportive friend or family member",
                "Engage in comforting rituals",
                "Look at photos or mementos if it helps",
                "Write a letter to the person or thing you lost"
            ],
            "daily_activities": [
                "Maintain basic self-care routines",
                "Allow time for both grief and normalcy",
                "Gentle exercise like walking",
                "Create a memorial or tribute",
                "Keep a grief journal"
            ],
            "social": [
                "Join a grief support group",
                "Share memories with others who knew the person",
                "Accept help from others",
                "Be honest about your needs",
                "Connect with others who've experienced similar loss"
            ],
            "therapeutic": [
                "Understand stages of grief (non-linear)",
                "Practice self-compassion",
                "Consider grief counseling or therapy",
                "Explore creative expression of grief",
                "Be patient with your healing process"
            ]
        },
        
        MentalState.STRESS: {
            "immediate": [
                "Take a 5-minute break",
                "Practice deep breathing",
                "Do a quick body scan meditation",
                "Step outside for fresh air",
                "Listen to calming music"
            ],
            "daily_activities": [
                "Prioritize and organize tasks",
                "Break large tasks into smaller steps",
                "Exercise regularly",
                "Maintain work-life boundaries",
                "Practice time management",
                "Get adequate sleep"
            ],
            "lifestyle": [
                "Learn to say 'no' to non-essential commitments",
                "Delegate tasks when possible",
                "Schedule regular breaks",
                "Maintain hobbies and interests",
                "Limit multitasking"
            ],
            "therapeutic": [
                "Practice mindfulness-based stress reduction",
                "Try yoga or tai chi",
                "Learn cognitive restructuring",
                "Consider stress management counseling",
                "Explore root causes of chronic stress"
            ]
        },
        
        MentalState.DEPRESSION: {
            "immediate": [
                "Get out of bed and open curtains for light",
                "Take a shower or bath",
                "Eat something nutritious",
                "Step outside, even briefly",
                "Reach out to someone you trust"
            ],
            "daily_activities": [
                "Establish and maintain a routine",
                "Set very small, achievable goals",
                "Exercise, even just 10 minutes of walking",
                "Get sunlight exposure daily",
                "Limit alcohol and avoid drugs",
                "Practice sleep hygiene"
            ],
            "social": [
                "Stay connected, even when you don't feel like it",
                "Ask for specific help from friends/family",
                "Join a support group",
                "Avoid isolation, even if you need alone time",
                "Be honest about your struggle with trusted people"
            ],
            "therapeutic": [
                "Seek professional help (therapy/psychiatry)",
                "Consider evidence-based therapies (CBT, DBT)",
                "Explore medication options with a doctor",
                "Practice behavioral activation",
                "Challenge negative thought patterns",
                "Be patient with recovery process"
            ]
        },
        
        MentalState.OVERWHELM: {
            "immediate": [
                "Stop and take 5 deep breaths",
                "Write down everything on your mind",
                "Choose ONE thing to focus on now",
                "Ask for help or extension if needed",
                "Remove yourself from overwhelming environment briefly"
            ],
            "organization": [
                "Brain dump all tasks onto paper",
                "Prioritize using urgent/important matrix",
                "Break tasks into tiny, manageable steps",
                "Use time-blocking for focused work",
                "Eliminate or delegate non-essential tasks"
            ],
            "daily_activities": [
                "Start mornings with simple routine",
                "Practice saying no to new commitments",
                "Schedule breaks throughout the day",
                "Simplify decisions (limit choices)",
                "Create systems to reduce decision fatigue"
            ],
            "therapeutic": [
                "Practice mindfulness to stay present",
                "Work with a therapist on capacity and boundaries",
                "Learn stress management techniques",
                "Address perfectionism if applicable",
                "Explore underlying anxiety or depression"
            ]
        }
    }
    
    @classmethod
    def get_strategies(cls, mental_state: MentalState) -> Dict[str, List[str]]:
        """Get all strategies for a mental state"""
        return cls.STRATEGIES.get(mental_state, {})
    
    @classmethod
    def get_immediate_strategies(cls, mental_state: MentalState) -> List[str]:
        """Get immediate coping strategies"""
        strategies = cls.STRATEGIES.get(mental_state, {})
        return strategies.get("immediate", [])
    
    @classmethod
    def get_all_strategies_list(cls, mental_state: MentalState) -> List[str]:
        """Get flattened list of all strategies"""
        strategies = cls.get_strategies(mental_state)
        all_strategies = []
        for category_strategies in strategies.values():
            all_strategies.extend(category_strategies)
        return all_strategies


# Export convenience function for easy access
def get_coping_strategies(mental_state: str, intensity: str = 'moderate') -> Dict[str, List[str]]:
    """
    Get coping strategies for a given mental state
    
    Args:
        mental_state: Mental state string (e.g., 'anxiety', 'sadness')
        intensity: Intensity level (not used currently, for future filtering)
    
    Returns:
        Dictionary of strategies by category
    """
    try:
        state_enum = MentalState(mental_state.lower())
        return CopingStrategiesDB.get_strategies(state_enum)
    except (ValueError, AttributeError):
        # Default to anxiety strategies if state not found
        return CopingStrategiesDB.get_strategies(MentalState.ANXIETY)
