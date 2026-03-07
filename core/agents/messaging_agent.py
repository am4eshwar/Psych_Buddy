"""
Messaging Agent - Handles communication, check-ins, and crisis detection
Uses Gemini 2.0 Flash for fast, empathetic communication
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from loguru import logger
import json

import google.generativeai as genai
from config import GOOGLE_API_KEY, CHECK_IN_TIMES
from config.mental_states import EMERGENCY_RESOURCES
from models import UserSession
from utils.prompts import MESSAGING_PROMPTS


class MessagingAgent:
    """
    Specialized agent for user communication and safety monitoring
    Responsibilities:
    - Deliver analysis reports and wellness plans
    - Conduct daily check-ins (4 times per day)
    - Monitor for crisis/emergency situations
    - Provide empathetic, supportive communication
    - Escalate urgent situations
    """
    
    def __init__(self, memory_manager, telegram_server):
        """Initialize Messaging Agent with Gemini 2.0 Flash"""
        logger.info("Initializing Messaging Agent...")
        
        self.memory = memory_manager
        self.telegram = telegram_server
        
        # Configure Gemini 2.0 Flash for fast, empathetic responses
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-exp',
            generation_config={
                'temperature': 0.9,  # Higher for more empathetic, varied responses
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 2048,
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
            ],
            system_instruction="""You are a compassionate mental wellness support agent. Your role is to:
1. Communicate with empathy, warmth, and understanding
2. Monitor for crisis situations and respond appropriately
3. Conduct check-ins in a gentle, non-judgmental way
4. Provide encouragement and emotional support
5. NEVER give medical advice - always recommend professional help when needed
6. Use emojis sparingly but appropriately to convey warmth
7. Keep messages concise but meaningful
8. Always prioritize user safety"""
        )
        
        logger.info("Messaging Agent initialized with Gemini 2.0 Flash")
    
    async def deliver_analysis_report(
        self,
        user_id: str,
        analysis: Dict[str, Any],
        wellness_plan: Dict[str, Any],
        music_recommendations: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Deliver initial analysis and wellness plan to user via Telegram
        
        Returns:
            Message sent to user
        """
        logger.info(f"Delivering analysis report to user {user_id}")
        
        try:
            # Build message generation prompt
            prompt = MESSAGING_PROMPTS['initial_report'].format(
                primary_state=analysis.get('primary_state', ''),
                intensity=analysis.get('intensity', ''),
                wellness_summary=wellness_plan.get('summary', ''),
                check_in_times=', '.join(CHECK_IN_TIMES),
                program_duration=wellness_plan.get('duration_days', 7)
            )
            
            # Generate empathetic message
            response = await self.model.generate_content_async(prompt)
            message = response.text
            
            # Add music recommendations if available
            if music_recommendations:
                music_section = f"\n\n🎵 **Music Therapy**\n{music_recommendations.get('therapeutic_guidance', '')}"
                if music_recommendations.get('playlist_url'):
                    music_section += f"\n\nPlaylist: {music_recommendations['playlist_url']}"
                message += music_section
            
            # Send via Telegram
            self.telegram.send_message(user_id, message)
            
            # Save to conversation history
            session = self.memory.get_active_session(user_id)
            if session:
                self.memory.save_conversation_message(
                    session.session_id,
                    'assistant',
                    message,
                    {'type': 'analysis_report'}
                )
            
            logger.info(f"Analysis report delivered to user {user_id}")
            return message
            
        except Exception as e:
            logger.error(f"Error delivering analysis report: {e}")
            raise
    
    async def conduct_check_in(
        self,
        session: UserSession,
        time_of_day: str,
        day_number: int
    ) -> str:
        """
        Conduct scheduled check-in with user
        
        Args:
            session: User session
            time_of_day: Time slot (morning/afternoon/evening/night)
            day_number: Day number in program (1-7)
        
        Returns:
            Check-in message sent
        """
        logger.info(f"Conducting check-in: Day {day_number}, {time_of_day}")
        
        try:
            # Get conversation context
            recent_history = self.memory.get_conversation_history(
                session.session_id,
                limit=10
            )
            
            # Determine check-in focus based on time
            focus_map = {
                '09:00': 'morning_energy',
                '13:00': 'midday_reflection',
                '17:00': 'evening_stress',
                '21:00': 'night_review'
            }
            focus = focus_map.get(time_of_day, 'general')
            
            # Build check-in prompt
            prompt = MESSAGING_PROMPTS['check_in'].format(
                day_number=day_number,
                time_of_day=time_of_day,
                focus_area=focus,
                primary_state=session.primary_state,
                recent_context=json.dumps(recent_history[-3:], indent=2) if recent_history else "First check-in"
            )
            
            # Generate check-in message
            response = await self.model.generate_content_async(prompt)
            message = response.text
            
            # Send via Telegram
            self.telegram.send_message(session.user_id, message)
            
            # Save to conversation
            self.memory.save_conversation_message(
                session.session_id,
                'assistant',
                message,
                {'type': 'check_in', 'day': day_number, 'time': time_of_day}
            )
            
            logger.info(f"Check-in conducted for session {session.session_id}")
            return message
            
        except Exception as e:
            logger.error(f"Error conducting check-in: {e}")
            raise
    
    async def process_user_response(
        self,
        session: UserSession,
        user_message: str
    ) -> str:
        """
        Process user's response during check-in or conversation
        
        Returns:
            Response message
        """
        logger.info(f"Processing user response for session {session.session_id}")
        
        try:
            # Save user message
            self.memory.save_conversation_message(
                session.session_id,
                'user',
                user_message
            )
            
            # Check for crisis indicators
            if self._detect_crisis_in_message(user_message):
                return await self._handle_crisis_situation(session, user_message)
            
            # Get conversation context
            conversation_history = self.memory.get_conversation_history(
                session.session_id,
                limit=15
            )
            
            # Build response prompt
            prompt = MESSAGING_PROMPTS['response'].format(
                user_message=user_message,
                session_state=session.primary_state,
                intensity=session.intensity,
                conversation_history=json.dumps(conversation_history, indent=2)
            )
            
            # Generate empathetic response
            response = await self.model.generate_content_async(prompt)
            message = response.text
            
            # Send via Telegram
            self.telegram.send_message(session.user_id, message)
            
            # Save assistant response
            self.memory.save_conversation_message(
                session.session_id,
                'assistant',
                message,
                {'type': 'conversation_response'}
            )
            
            logger.info(f"Response sent to user {session.user_id}")
            return message
            
        except Exception as e:
            logger.error(f"Error processing user response: {e}")
            raise
    
    async def send_task_reminder(
        self,
        session: UserSession,
        task: Dict[str, Any]
    ) -> str:
        """
        Send wellness task reminder
        
        Returns:
            Reminder message sent
        """
        logger.info(f"Sending task reminder for session {session.session_id}")
        
        try:
            # Build reminder prompt
            prompt = MESSAGING_PROMPTS['task_reminder'].format(
                task_title=task.get('title', ''),
                task_description=task.get('description', ''),
                task_duration=task.get('duration', 30)
            )
            
            # Generate motivational reminder
            response = await self.model.generate_content_async(prompt)
            message = response.text
            
            # Send via Telegram
            self.telegram.send_message(session.user_id, message)
            
            # Save to conversation
            self.memory.save_conversation_message(
                session.session_id,
                'assistant',
                message,
                {'type': 'task_reminder', 'task_id': task.get('id')}
            )
            
            logger.info(f"Task reminder sent to user {session.user_id}")
            return message
            
        except Exception as e:
            logger.error(f"Error sending task reminder: {e}")
            raise
    
    async def send_progress_update(
        self,
        session: UserSession,
        progress_analysis: Dict[str, Any]
    ) -> str:
        """
        Send progress update to user
        
        Returns:
            Progress message sent
        """
        logger.info(f"Sending progress update for session {session.session_id}")
        
        try:
            # Build progress message prompt
            prompt = MESSAGING_PROMPTS['progress_update'].format(
                progress_score=progress_analysis.get('progress_score', 0),
                improvements=json.dumps(progress_analysis.get('improvements', [])),
                concerns=json.dumps(progress_analysis.get('concerns', [])),
                day_number=len(session.mood_scores) // 4  # 4 check-ins per day
            )
            
            # Generate encouraging message
            response = await self.model.generate_content_async(prompt)
            message = response.text
            
            # Send via Telegram
            self.telegram.send_message(session.user_id, message)
            
            # Save to conversation
            self.memory.save_conversation_message(
                session.session_id,
                'assistant',
                message,
                {'type': 'progress_update'}
            )
            
            logger.info(f"Progress update sent to user {session.user_id}")
            return message
            
        except Exception as e:
            logger.error(f"Error sending progress update: {e}")
            raise
    
    def _detect_crisis_in_message(self, message: str) -> bool:
        """Detect crisis indicators in user message"""
        crisis_keywords = [
            'suicide', 'kill myself', 'end my life', 'self-harm', 'hurt myself',
            'no reason to live', 'better off dead', 'want to die', 'can\'t go on',
            'hopeless', 'give up', 'end it all'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in crisis_keywords)
    
    async def _handle_crisis_situation(
        self,
        session: UserSession,
        user_message: str
    ) -> str:
        """Handle crisis situation with immediate intervention"""
        logger.critical(f"CRISIS DETECTED for user {session.user_id}")
        
        crisis_message = f"""🆘 **I'm very concerned about what you've shared.**

Your safety is the absolute top priority right now. Please know that you're not alone, and there are people who want to help you immediately.

**Please reach out to crisis support RIGHT NOW:**

{EMERGENCY_RESOURCES}

These services are:
✓ Available 24/7
✓ Free and confidential
✓ Staffed by trained professionals
✓ There to support you through this

**You matter. Your life has value. Please reach out for help.**

I'm here too, but professional crisis support is crucial right now. Would you like me to help you find additional local resources?"""
        
        # Send immediately via Telegram
        self.telegram.send_message(session.user_id, crisis_message)
        
        # Mark session as high-risk
        session.metadata = session.metadata or {}
        session.metadata['crisis_detected'] = True
        session.metadata['crisis_timestamp'] = datetime.utcnow().isoformat()
        self.memory.save_session(session)
        
        # Save to conversation
        self.memory.save_conversation_message(
            session.session_id,
            'assistant',
            crisis_message,
            {'type': 'crisis_intervention', 'severity': 'high'}
        )
        
        logger.critical(f"Crisis intervention message sent to user {session.user_id}")
        return crisis_message