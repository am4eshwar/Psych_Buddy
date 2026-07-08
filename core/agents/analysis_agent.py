"""
Analysis Agent - Handles emotional analysis, wellness planning, and resource coordination
Uses Gemini 2.5 Flash for deep analytical reasoning
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
from loguru import logger
import json
import uuid

import google.generativeai as genai
from config import GOOGLE_API_KEY, GEMINI_MODEL, PROGRAM_DURATION_DAYS
from config.mental_states import MentalState
from models import UserProfile, UserSession
from utils.prompts import ANALYSIS_PROMPTS
from utils.coping_strategies import get_coping_strategies


class AnalysisAgent:
    """
    Specialized agent for emotional analysis and wellness planning
    Responsibilities:
    - Analyze user's mental state and emotional condition
    - Assess crisis situations
    - Generate personalized wellness plans
    - Coordinate calendar scheduling
    - Curate therapeutic music playlists
    """
    
    def __init__(self, memory_manager):
        """Initialize Analysis Agent with Gemini 2.5 Flash"""
        logger.info("Initializing Analysis Agent...")
        
        self.memory = memory_manager
        
        # Configure Gemini 2.5 Flash for deep analysis
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            generation_config={
                'temperature': 0.7,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 8192,
            },
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
        )
        
        logger.info("Analysis Agent initialized with Gemini 2.5 Flash")
    
    async def analyze_initial_input(
        self,
        user_input: str,
        user_id: str,
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """
        Analyze user's initial input to understand their mental state
        
        Returns:
            {
                'primary_state': str,
                'secondary_states': List[str],
                'intensity': str,
                'triggers': List[str],
                'is_crisis': bool,
                'risk_level': str,
                'session': UserSession,
                'reasoning': str
            }
        """
        logger.info(f"Analyzing initial input for user {user_id}")
        
        try:
            # Build analysis prompt
            prompt = ANALYSIS_PROMPTS['initial_analysis'].format(
                user_input=user_input,
                available_states=', '.join([state.value for state in MentalState]),
                user_history=await self._get_user_history_summary(user_id)
            )
            
            # Generate analysis using Gemini
            response = await self.model.generate_content_async(prompt)
            analysis_text = response.text
            
            # Parse JSON response
            analysis = self._parse_json_response(analysis_text)
            
            # Check for crisis
            is_crisis = self._detect_crisis(user_input, analysis)
            
            # Create session
            triggers = analysis.get('triggers', [])
            trigger_str = ', '.join(triggers) if isinstance(triggers, list) else str(triggers)
            
            session = UserSession(
                session_id=str(uuid.uuid4()),
                user_id=user_id,
                primary_mental_state=analysis.get('primary_state', 'anxiety'),
                secondary_mental_states=analysis.get('secondary_states', []),
                intensity=analysis.get('intensity', 'moderate'),
                trigger_event=trigger_str,
                context="Initial Analysis",
                initial_prompt=user_input,
                start_date=datetime.now(timezone.utc),
                duration_days=PROGRAM_DURATION_DAYS,
                is_active=True
            )
            
            # Save session to memory
            await self.memory.save_session(session)
            
            # Save conversation
            await self.memory.save_turn(
                user_id,
                'user',
                user_input,
                session.session_id
            )
            
            logger.info(f"Analysis complete: {session.primary_mental_state} ({session.intensity})")
            
            return {
                'primary_state': session.primary_mental_state,
                'secondary_states': session.secondary_mental_states,
                'intensity': session.intensity,
                'triggers': session.trigger_event,
                'is_crisis': is_crisis,
                'risk_level': analysis.get('risk_level', 'low'),
                'session': session,
                'reasoning': analysis.get('reasoning', '')
            }
            
        except Exception as e:
            logger.error(f"Error in initial analysis: {e}")
            raise
    
    async def generate_wellness_plan(self, session: UserSession) -> Dict[str, Any]:
        """
        Generate personalized wellness plan based on analysis
        
        Returns:
            {
                'summary': str,
                'daily_themes': List[Dict],
                'tasks': List[Dict],
                'coping_strategies': List[str],
                'professional_recommendation': bool
            }
        """
        logger.info(f"Generating wellness plan for session {session.session_id}")
        
        try:
            # Get coping strategies from database
            strategies = get_coping_strategies(session.primary_mental_state, session.intensity)
            
            # Build prompt
            prompt = ANALYSIS_PROMPTS['wellness_plan'].format(
                primary_state=session.primary_mental_state,
                secondary_states=', '.join([str(s) for s in session.secondary_mental_states]),
                intensity=session.intensity,
                triggers=session.trigger_event,
                duration_days=session.duration_days,
                coping_strategies=json.dumps(strategies, indent=2)
            )
            
            # Generate plan using Gemini
            response = await self.model.generate_content_async(prompt)
            plan_text = response.text
            
            # Parse plan
            plan = self._parse_json_response(plan_text)
            
            # Save plan to session
            session.wellness_plan = plan
            await self.memory.save_session(session)
            
            logger.info(f"Wellness plan generated with {len(plan.get('tasks', []))} tasks")
            
            return plan
            
        except Exception as e:
            logger.error(f"Error generating wellness plan: {e}")
            raise
    
    async def schedule_calendar_events(
        self,
        session: UserSession,
        wellness_plan: Dict[str, Any],
        calendar_server
    ) -> List[str]:
        """
        Coordinate with calendar to schedule wellness activities
        
        Returns:
            List of created event IDs
        """
        logger.info(f"Scheduling calendar events for session {session.session_id}")
        
        event_ids = []
        
        try:
            tasks = wellness_plan.get('tasks', [])
            
            for task in tasks:
                # Parse task timing
                day_number = task.get('day', 1)
                time_slot = task.get('time_slot', '09:00')
                
                # Calculate scheduled time
                scheduled_date = session.start_date + timedelta(days=day_number - 1)
                hour, minute = map(int, time_slot.split(':'))
                scheduled_time = scheduled_date.replace(hour=hour, minute=minute)
                
                # Create calendar event
                event_id = calendar_server.create_event(
                    summary=f"🧘 {task.get('title', 'Wellness Task')}",
                    description=task.get('description', ''),
                    start_time=scheduled_time,
                    duration_minutes=task.get('duration', 30),
                    reminders=[15, 60]
                )
                
                if event_id:
                    event_ids.append(event_id)
                    logger.info(f"Created calendar event: {task.get('title')}")
            
            logger.info(f"Scheduled {len(event_ids)} calendar events")
            return event_ids
            
        except Exception as e:
            logger.error(f"Error scheduling calendar events: {e}")
            return event_ids
    
    async def curate_music_playlist(
        self,
        session: UserSession,
        spotify_server
    ) -> Dict[str, Any]:
        """
        Curate therapeutic music playlist based on mental state
        
        Returns:
            {
                'playlist_id': str,
                'playlist_url': str,
                'tracks': List[Dict],
                'therapeutic_guidance': str
            }
        """
        logger.info(f"Curating music playlist for session {session.session_id}")
        
        try:
            # Build music curation prompt
            prompt = ANALYSIS_PROMPTS['music_therapy'].format(
                primary_state=session.primary_mental_state,
                intensity=session.intensity,
                time_of_day='morning'  # Can be dynamic
            )
            
            # Get AI guidance on music therapy
            response = await self.model.generate_content_async(prompt)
            guidance = self._parse_json_response(response.text)
            
            # Get recommendations from Spotify
            recommendations = spotify_server.get_mood_recommendations(
                session.primary_state,
                session.intensity
            )
            
            result = {
                'playlist_url': recommendations.get('playlist_url', ''),
                'tracks': recommendations.get('tracks', []),
                'therapeutic_guidance': guidance.get('guidance', ''),
                'suggested_activities': guidance.get('activities', [])
            }
            
            logger.info("Music playlist curated with therapeutic guidance")
            return result
            
        except Exception as e:
            logger.error(f"Error curating music playlist: {e}")
            return {}
    
    async def analyze_progress(self, session: UserSession) -> Dict[str, Any]:
        """
        Analyze user's progress and adjust plan if needed
        
        Returns:
            {
                'progress_score': float,
                'improvements': List[str],
                'concerns': List[str],
                'plan_adjustments': Dict,
                'continue_program': bool
            }
        """
        logger.info(f"Analyzing progress for session {session.session_id}")
        
        try:
            # Get conversation history
            history = await self.memory.get_conversation_history(
                session.user_id, limit=20
            )
            # Build progress analysis prompt
            prompt = ANALYSIS_PROMPTS['progress_analysis'].format(
                session_data=session.model_dump_json(indent=2),
                conversation_history=json.dumps(history[-20:], indent=2),
                mood_scores=session.mood_scores
            )
            
            # Generate analysis
            response = await self.model.generate_content_async(prompt)
            analysis = self._parse_json_response(response.text)
            
            logger.info(f"Progress analysis complete: score {analysis.get('progress_score', 0)}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing progress: {e}")
            raise
    
    def _detect_crisis(self, user_input: str, analysis: Dict) -> bool:
        """Detect crisis situations requiring immediate intervention"""
        crisis_keywords = [
            'suicide', 'kill myself', 'end my life', 'self-harm', 'hurt myself',
            'no reason to live', 'better off dead', 'want to die'
        ]
        
        user_input_lower = user_input.lower()
        
        # Check for crisis keywords
        has_crisis_keyword = any(keyword in user_input_lower for keyword in crisis_keywords)
        
        # Check risk level from analysis
        high_risk = analysis.get('risk_level', '').lower() in ['high', 'severe', 'critical']
        
        return has_crisis_keyword or high_risk
    
    async def _get_user_history_summary(self, user_id: str) -> str:
        """Get summary of user's previous sessions"""
        try:
            sessions = await self.memory.get_user_sessions(user_id)
            if not sessions:
                return "No previous history"
            
            summary = f"Previous sessions: {len(sessions)}\n"
            for session in sessions[-3:]:  # Last 3 sessions
                summary += f"- {session.primary_state} ({session.intensity})\n"
            
            return summary
        except Exception:
            return "No previous history"
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from AI response"""
        try:
            # Try to find JSON in response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            
            return {}
        except Exception as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return {}