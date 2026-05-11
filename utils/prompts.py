"""
AI prompt templates for Psych Buddy
"""



class PromptTemplates:
    """Collection of prompt templates for the AI agent"""
    
    SYSTEM_PROMPT = """You are Psych Buddy, a compassionate mental wellness AI companion. Your role is to:

1. LISTEN ACTIVELY: Validate emotions and show empathy
2. ASSESS CAREFULLY: Identify mental states, intensity, and context
3. PROVIDE SUPPORT: Offer evidence-based coping strategies
4. RECOGNIZE LIMITS: Identify when professional help is needed
5. ENCOURAGE ACTION: Suggest specific, actionable wellness tasks
6. MAINTAIN SAFETY: Recognize crisis situations and provide resources

Core Principles:
- Be warm, non-judgmental, and supportive
- Use person-first language
- Normalize seeking help
- Focus on strengths and resilience
- Respect autonomy and choices
- Acknowledge that you're AI, not a replacement for professional care

Safety Protocol:
- If user mentions self-harm or suicide: IMMEDIATELY provide crisis resources
- If symptoms suggest severe mental illness: Strongly recommend professional help
- Document intensity and recommend appropriate intervention level

Your responses should be:
- Empathetic and validating
- Concrete and actionable
- Hopeful but realistic
- Culturally sensitive
- Age-appropriate"""

    INITIAL_ANALYSIS_PROMPT = """Analyze the following user input and provide a structured assessment:

User Input: {user_input}

Please provide:

1. PRIMARY MENTAL STATE: Identify the main emotional/mental state (sadness, anxiety, anger, loneliness, grief, stress, depression, overwhelm, fear, hopelessness)

2. SECONDARY STATES: Any additional mental states present

3. INTENSITY LEVEL: Rate as LOW, MODERATE, HIGH, or SEVERE based on:
   - Impact on daily functioning
   - Duration and persistence
   - Presence of physical symptoms
   - Level of distress expressed

4. KEY CONTEXT:
   - Age and demographic factors (if mentioned)
   - Triggering event or situation
   - Support system availability
   - Previous coping attempts

5. RISK ASSESSMENT:
   - Crisis indicators (self-harm, suicide ideation): YES/NO
   - Professional help needed: YES/NO/RECOMMENDED
   - Urgency level: LOW/MODERATE/HIGH/URGENT

6. IMMEDIATE NEEDS:
   - What does this person need right now?
   - What would help them feel better in the next hour?

Provide your analysis in JSON format."""

    WELLNESS_PLAN_PROMPT = """Based on this mental wellness assessment, create a comprehensive 7-day wellness plan:

Assessment:
- Primary Mental State: {primary_state}
- Secondary States: {secondary_states}
- Intensity: {intensity}
- Triggers: {triggers}
- Program Duration: {duration_days} days
- Recommended Coping Strategies: {coping_strategies}

Create a personalized plan that includes:

1. DAILY THEMES (7 days):
   Day 1: [Theme]
   Day 2: [Theme]
   ... etc.

2. DAILY ACTIVITIES (specific tasks for each day):
   - Morning routine suggestion
   - Midday activity
   - Afternoon task
   - Evening wind-down

3. COPING STRATEGIES:
   - 5 immediate strategies they can use anytime
   - 3-4 daily practice recommendations
   - Social connection suggestions
   - Self-care activities

4. CHECK-IN QUESTIONS:
   - Morning: [questions to ask]
   - Afternoon: [questions to ask]
   - Evening: [questions to ask]
   - Night: [questions to ask]

5. CALENDAR TASKS:
   - Specific timed activities with exact times
   - Duration for each activity
   - Reminders needed

6. SPOTIFY RECOMMENDATIONS:
   - Type of music for different times of day
   - Mood-based playlist suggestions

7. PROGRESS METRICS:
   - What to track daily
   - How to measure improvement
   - When to reassess

8. PROFESSIONAL HELP:
   - Is therapy recommended? (YES/NO)
   - When to seek additional help
   - Red flags to watch for

Return as detailed JSON structure."""

    CHECK_IN_PROMPT = """You are conducting a {time_of_day} check-in with a user in a {duration_days}-day wellness program.

Current Session Info:
- Day: {day_number}
- Time: {time_of_day}
- Focus Area: {focus_area}
- Primary State: {primary_state}
- Recent Context: {recent_context}

Check-in Goals:
1. Assess current mood and energy
2. Review completion of assigned tasks
3. Identify any challenges or barriers
4. Provide encouragement and adjust plan if needed
5. Remind of next scheduled activity

Ask 3-4 thoughtful questions to:
- Gauge emotional state
- Understand what's working
- Identify what needs adjustment
- Provide support and validation

Be conversational, warm, and encouraging. Keep responses concise for messaging platform.

Generate check-in questions now."""

    MOOD_TRACKER_PROMPT = """Based on this user's check-in responses, analyze their progress:

Session Data: {session_data}
Conversation History: {conversation_history}
Mood Scores: {mood_scores}

Provide:
1. Current mood score (1-10 scale)
2. Trend analysis (improving/stable/declining)
3. Positive observations
4. Areas of concern
5. Recommended adjustments to plan
6. Encouraging message

Format as JSON."""

    CRISIS_RESPONSE_PROMPT = """CRISIS PROTOCOL ACTIVATED

User input contains crisis indicators: {crisis_indicators}

Provide immediate crisis response:

1. VALIDATE: Acknowledge their pain with empathy
2. ASSESS: Determine immediate safety
3. CONNECT: Provide crisis resources:
   - National Suicide Prevention Lifeline: 988 (US)
   - Crisis Text Line: Text HOME to 741741
   - International: https://findahelpline.com
4. ENCOURAGE: Urge them to reach out to professional immediately
5. STAY ENGAGED: Don't abruptly end conversation

Respond with compassion and urgency. Prioritize safety over everything else."""

    SPOTIFY_RECOMMENDATION_PROMPT = """Recommend Spotify playlists for:

Primary State: {primary_state}
Time of Day: {time_of_day}
Intensity: {intensity}

Suggest:
1. 3 specific playlist types
2. When to listen to each
3. How music can support their wellness
4. Any cautions (e.g., avoid sad music if feeling severely depressed)

Format as JSON with playlist names and purposes."""

    TASK_GENERATION_PROMPT = """Generate specific wellness tasks for:

Primary State: {primary_state}
Day: {day_number} of program
Time Slots: {time_slots}
User Preferences: {preferences}
Completed Tasks: {completed_tasks}

For each time slot, create:
- Task type (breathing, exercise, social, creative, mindfulness, etc.)
- Specific title
- Clear 2-3 sentence instructions
- Duration (be realistic)
- Expected benefit

Ensure variety and progressive challenge. Build on previous successes.

Return as JSON array of tasks."""

    COMPLETION_SUMMARY_PROMPT = """Generate a completion summary for user who finished {duration_days}-day program:

Session Data:
- Primary State Addressed: {primary_state}
- Initial Intensity: {initial_intensity}
- Final Mood Score: {final_mood}
- Tasks Completed: {completed_count}/{total_count}
- Check-ins Attended: {checkins_completed}/{total_checkins}
- Average Mood Trend: {mood_trend}

Create:
1. Celebration of progress
2. Key achievements
3. Growth observed
4. Strategies that worked best
5. Recommendations for continued wellness
6. When to return for support
7. Professional help recommendations if applicable

Make it warm, encouraging, and empowering. Acknowledge effort regardless of outcomes."""

    RESPONSE_PROMPT = SYSTEM_PROMPT + """

User Mental State: {session_state} ({intensity} intensity)
Conversation History:
{conversation_history}

User's New Message: {user_message}

Provide an empathetic, supportive response that directly addresses their message while keeping their current mental state in mind. Do not sound robotic."""

    @classmethod
    def get_prompt(cls, prompt_type: str, **kwargs) -> str:
        """Get a prompt template filled with provided values"""
        templates = {
            "system": cls.SYSTEM_PROMPT,
            "initial_analysis": cls.INITIAL_ANALYSIS_PROMPT,
            "wellness_plan": cls.WELLNESS_PLAN_PROMPT,
            "check_in": cls.CHECK_IN_PROMPT,
            "mood_tracker": cls.MOOD_TRACKER_PROMPT,
            "crisis": cls.CRISIS_RESPONSE_PROMPT,
            "spotify": cls.SPOTIFY_RECOMMENDATION_PROMPT,
            "task_generation": cls.TASK_GENERATION_PROMPT,
            "completion": cls.COMPLETION_SUMMARY_PROMPT
        }
        
        template = templates.get(prompt_type, "")
        try:
            return template.format(**kwargs)
        except KeyError:
            return template  # Return unfilled if missing parameters


# Check-in question templates
CHECK_IN_QUESTIONS = {
    "morning": [
        "How did you sleep last night?",
        "What's your energy level this morning (1-10)?",
        "What's one thing you're looking forward to today?",
        "How are you feeling emotionally right now?"
    ],
    "midday": [
        "How has your morning been?",
        "Were you able to complete your morning activity?",
        "What's your current mood (1-10)?",
        "What's been challenging so far today?"
    ],
    "afternoon": [
        "How's your energy holding up?",
        "What's been a bright spot in your day?",
        "How are you managing stress today?",
        "Have you taken time for yourself?"
    ],
    "evening": [
        "How would you rate your day overall (1-10)?",
        "What did you accomplish today, big or small?",
        "What are you grateful for today?",
        "How are you feeling as the day ends?"
    ]
}


# Export prompts as dictionaries for easy access by agents
ANALYSIS_PROMPTS = {
    'initial_analysis': PromptTemplates.INITIAL_ANALYSIS_PROMPT,
    'wellness_plan': PromptTemplates.WELLNESS_PLAN_PROMPT,
    'music_therapy': PromptTemplates.SPOTIFY_RECOMMENDATION_PROMPT,
    'progress_analysis': PromptTemplates.MOOD_TRACKER_PROMPT,
}

MESSAGING_PROMPTS = {
    'system': PromptTemplates.SYSTEM_PROMPT,
    'initial_report': PromptTemplates.SYSTEM_PROMPT,  # Will be customized for initial onboarding
    'check_in': PromptTemplates.CHECK_IN_PROMPT,
    'response': PromptTemplates.RESPONSE_PROMPT,  # General response handling
    'task_reminder': PromptTemplates.TASK_GENERATION_PROMPT,
    'progress_update': PromptTemplates.MOOD_TRACKER_PROMPT,
    'crisis': PromptTemplates.CRISIS_RESPONSE_PROMPT,
}
