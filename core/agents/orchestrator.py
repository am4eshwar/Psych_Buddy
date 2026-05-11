"""
Agent Orchestrator - Coordinates Analysis and Messaging agents
"""
from typing import Dict, Any, Optional
from loguru import logger
from datetime import datetime

from core.agents.analysis_agent import AnalysisAgent
from core.agents.messaging_agent import MessagingAgent
from models import UserProfile, UserSession


class AgentOrchestrator:
    """
    Orchestrates collaboration between Analysis and Messaging agents
    Ensures seamless workflow and information exchange
    """
    
    def __init__(
        self,
        memory_manager,
        telegram_server,
        calendar_server=None,
        spotify_server=None
    ):
        """Initialize orchestrator with both agents"""
        logger.info("Initializing Agent Orchestrator...")
        
        self.memory = memory_manager
        self.calendar = calendar_server
        self.spotify = spotify_server
        
        # Initialize specialized agents
        self.analysis_agent = AnalysisAgent(memory_manager)
        self.messaging_agent = MessagingAgent(memory_manager, telegram_server)
        
        logger.info("Agent Orchestrator initialized with 2 specialized agents")
    
    async def handle_new_user_input(
        self,
        user_id: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Orchestrate handling of new user input
        Flow: Analysis Agent analyzes → Messaging Agent delivers
        
        Returns:
            Result dictionary with session and messages
        """
        logger.info(f"Orchestrating new user input from {user_id}")
        
        try:
            # Step 1: Get or create user profile
            user_profile = await self.memory.get_user_profile(user_id)
            if not user_profile:
                user_profile = UserProfile(user_id=user_id)
                await self.memory.save_user_profile(user_profile)
            
            # Step 2: Analysis Agent analyzes the input
            logger.info("→ Analysis Agent: Analyzing user condition...")
            analysis = await self.analysis_agent.analyze_initial_input(
                user_message,
                user_id,
                user_profile
            )
            
            # Step 3: Check for crisis
            if analysis['is_crisis']:
                logger.warning("Crisis detected - Messaging Agent handling immediately")
                crisis_message = await self.messaging_agent._handle_crisis_situation(
                    analysis['session'],
                    user_message
                )
                return {
                    'session': analysis['session'],
                    'is_crisis': True,
                    'message': crisis_message
                }
            
            # Step 4: Analysis Agent generates wellness plan
            logger.info("→ Analysis Agent: Generating personalized wellness plan...")
            wellness_plan = await self.analysis_agent.generate_wellness_plan(
                analysis['session']
            )
            
            # Step 5: Analysis Agent schedules calendar if available
            if self.calendar:
                logger.info("→ Analysis Agent: Scheduling calendar events...")
                await self.analysis_agent.schedule_calendar_events(
                    analysis['session'],
                    wellness_plan,
                    self.calendar
                )
            
            # Step 6: Analysis Agent curates music playlist if available
            music_recommendations = None
            if self.spotify:
                logger.info("→ Analysis Agent: Curating therapeutic music...")
                music_recommendations = await self.analysis_agent.curate_music_playlist(
                    analysis['session'],
                    self.spotify
                )
            
            # Step 7: Messaging Agent delivers comprehensive report
            logger.info("→ Messaging Agent: Delivering analysis report to user...")
            message = await self.messaging_agent.deliver_analysis_report(
                user_id,
                analysis,
                wellness_plan,
                music_recommendations
            )
            
            logger.info("✓ Orchestration complete - User session started")
            
            return {
                'session': analysis['session'],
                'analysis': analysis,
                'wellness_plan': wellness_plan,
                'music_recommendations': music_recommendations,
                'message': message,
                'is_crisis': False
            }
            
        except Exception as e:
            logger.error(f"Error in orchestration: {e}")
            raise
    
    async def handle_check_in(
        self,
        session_id: str,
        time_of_day: str,
        day_number: int
    ):
        """
        Orchestrate scheduled check-in
        Flow: Messaging Agent conducts check-in
        """
        logger.info(f"Orchestrating check-in: Day {day_number}, {time_of_day}")
        
        try:
            # Get session
            session = await self.memory.get_session(session_id)
            if not session:
                logger.error(f"Session {session_id} not found")
                return
            
            # Messaging Agent conducts check-in
            logger.info("→ Messaging Agent: Conducting check-in...")
            await self.messaging_agent.conduct_check_in(
                session,
                time_of_day,
                day_number
            )
            
            logger.info("✓ Check-in completed")
            
        except Exception as e:
            logger.error(f"Error in check-in orchestration: {e}")
    
    async def handle_user_response(
        self,
        user_id: str,
        user_message: str
    ) -> str:
        """
        Orchestrate user response during conversation
        Flow: Messaging Agent responds → Analysis Agent tracks progress (if needed)
        
        Returns:
            Response message
        """
        logger.info(f"Orchestrating user response from {user_id}")
        
        try:
            # Get active session
            session = await self.memory.get_active_session(user_id)
            if not session:
                logger.warning(f"No active session for user {user_id}")
                return "I don't have an active session for you. Please type /start to begin."
            
            # Messaging Agent processes response
            logger.info("→ Messaging Agent: Processing response...")
            response = await self.messaging_agent.process_user_response(
                session,
                user_message
            )
            
            # Check if progress analysis needed (every 7 check-ins = ~2 days)
            if len(session.mood_scores) > 0 and len(session.mood_scores) % 7 == 0:
                logger.info("→ Analysis Agent: Analyzing progress...")
                progress = await self.analysis_agent.analyze_progress(session)
                
                # Messaging Agent sends progress update
                logger.info("→ Messaging Agent: Sending progress update...")
                await self.messaging_agent.send_progress_update(session, progress)
            
            logger.info("✓ Response handled")
            return response
            
        except Exception as e:
            logger.error(f"Error handling user response: {e}")
            return "I apologize, I encountered an error. Please try again."
    
    async def handle_task_reminder(
        self,
        task_id: str,
        session_id: str
    ):
        """
        Orchestrate task reminder
        Flow: Messaging Agent sends reminder
        """
        logger.info(f"Orchestrating task reminder {task_id}")
        
        try:
            # Get session
            session = await self.memory.get_session(session_id)
            if not session:
                return
            
            # Find task
            task = None
            for t in session.wellness_plan.get('tasks', []):
                if t.get('id') == task_id:
                    task = t
                    break
            
            if not task:
                logger.warning(f"Task {task_id} not found")
                return
            
            # Messaging Agent sends reminder
            logger.info("→ Messaging Agent: Sending task reminder...")
            await self.messaging_agent.send_task_reminder(session, task)
            
            logger.info("✓ Task reminder sent")
            
        except Exception as e:
            logger.error(f"Error in task reminder orchestration: {e}")