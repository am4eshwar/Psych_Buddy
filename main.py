"""
Mental Wellness AI Agent - Multi-Agent System
Orchestrates Analysis Agent and Messaging Agent
Telegram-only communication platform
"""
import sys
import argparse
from loguru import logger

from config import (
    validate_config,
    LOG_LEVEL,
    LOGS_DIR,
    PROGRAM_DURATION_DAYS
)
from core.memory import VertexMemoryManager
from core.scheduler import WellnessScheduler
from core.agents import AgentOrchestrator
from mcp import (
    TelegramMCPServer,
    GoogleCalendarMCPServer,
    SpotifyMCPServer
)


# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    level=LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
)
logger.add(
    LOGS_DIR / "wellness_agent_{time}.log",
    rotation="1 day",
    retention="7 days",
    level=LOG_LEVEL
)


class MentalWellnessApp:
    """
    Mental Wellness Multi-Agent Application
    
    Architecture:
    - Analysis Agent: Emotional analysis, wellness planning, resource coordination
    - Messaging Agent: Communication, check-ins, crisis detection
    - Orchestrator: Coordinates agent collaboration
    """
    
    def __init__(self):
        """Initialize the Multi-Agent Mental Wellness Application"""
        logger.info("=" * 70)
        logger.info("Initializing Mental Wellness Multi-Agent System")
        logger.info("=" * 70)
        
        # Validate configuration
        try:
            validate_config()
            logger.info("✓ Configuration validated")
        except ValueError as e:
            logger.error(f"✗ Configuration validation failed: {e}")
            raise
        
        # Initialize memory system (Vertex AI)
        logger.info("Initializing Vertex AI Memory Store...")
        self.memory = VertexMemoryManager()
        logger.info("✓ Memory system initialized")
        
        # Initialize MCP servers
        logger.info("Initializing MCP Servers...")
        
        # Telegram (required)
        try:
            self.telegram_server = TelegramMCPServer()
            logger.info("✓ Telegram server initialized")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Telegram: {e}")
            raise
        
        # Google Calendar (optional)
        self.calendar_server = None
        try:
            self.calendar_server = GoogleCalendarMCPServer()
            logger.info("✓ Google Calendar server initialized")
        except Exception as e:
            logger.warning(f"⚠ Google Calendar not available: {e}")
        
        # Spotify (optional)
        self.spotify_server = None
        try:
            self.spotify_server = SpotifyMCPServer()
            logger.info("✓ Spotify server initialized")
        except Exception as e:
            logger.warning(f"⚠ Spotify not available: {e}")
        
        # Initialize Agent Orchestrator (coordinates Analysis + Messaging agents)
        logger.info("Initializing Multi-Agent Orchestrator...")
        self.orchestrator = AgentOrchestrator(
            memory_manager=self.memory,
            telegram_server=self.telegram_server,
            calendar_server=self.calendar_server,
            spotify_server=self.spotify_server
        )
        logger.info("✓ Agent orchestrator initialized")
        logger.info("  → Analysis Agent: Ready (Gemini 2.0 Flash Thinking)")
        logger.info("  → Messaging Agent: Ready (Gemini 2.0 Flash)")
        
        # Initialize scheduler
        logger.info("Initializing wellness scheduler...")
        self.scheduler = WellnessScheduler(self.memory)
        self.scheduler.register_check_in_callback("default", self.handle_check_in)
        self.scheduler.register_task_callback("default", self.handle_task_reminder)
        logger.info("✓ Scheduler initialized")
        
        # Register Telegram message handler
        self.telegram_server.register_message_handler(self.handle_user_message)
        
        logger.info("=" * 70)
        logger.info("Mental Wellness Multi-Agent System Ready!")
        logger.info("=" * 70)
    
    async def handle_user_message(self, user_id: str, message: str) -> str:
        """
        Handle incoming message from user via Telegram
        Routes to orchestrator which coordinates both agents
        
        Args:
            user_id: Telegram chat_id
            message: User message
            
        Returns:
            Response message
        """
        logger.info(f"📨 Message received from user {user_id}")
        logger.debug(f"Message content: {message[:100]}...")
        
        try:
            # Check if user has active session
            active_session = self.memory.get_active_session(user_id)
            
            if not active_session:
                # New user - orchestrate full onboarding
                logger.info("→ New user detected - Starting multi-agent onboarding")
                result = await self.orchestrator.handle_new_user_input(user_id, message)
                
                # Schedule check-ins for new session
                if not result.get('is_crisis'):
                    self.scheduler.schedule_daily_check_ins(result['session'])
                    logger.info(f"✓ Scheduled {PROGRAM_DURATION_DAYS * 4} check-ins")
                
                return result['message']
            else:
                # Existing user - handle response
                logger.info("→ Existing user - Processing response")
                response = await self.orchestrator.handle_user_response(user_id, message)
                return response
                
        except Exception as e:
            logger.error(f"✗ Error handling user message: {e}", exc_info=True)
            return "I apologize, but I encountered an error. Please try again or type /start to begin a new session."
    
    async def handle_check_in(self, session_id: str, time_of_day: str, day_number: int):
        """
        Handle scheduled check-in
        Delegates to orchestrator which uses Messaging Agent
        
        Args:
            session_id: Session identifier
            time_of_day: Time slot for check-in
            day_number: Day number in program
        """
        logger.info(f"⏰ Check-in triggered: Session {session_id}, Day {day_number}, {time_of_day}")
        
        try:
            await self.orchestrator.handle_check_in(session_id, time_of_day, day_number)
            logger.info("✓ Check-in completed successfully")
        except Exception as e:
            logger.error(f"✗ Error in check-in: {e}", exc_info=True)
    
    async def handle_task_reminder(self, task_id: str, session_id: str):
        """
        Handle task reminder
        Delegates to orchestrator which uses Messaging Agent
        
        Args:
            task_id: Task identifier
            session_id: Session identifier
        """
        logger.info(f"📋 Task reminder triggered: {task_id}")
        
        try:
            await self.orchestrator.handle_task_reminder(task_id, session_id)
            logger.info("✓ Task reminder sent successfully")
        except Exception as e:
            logger.error(f"✗ Error sending task reminder: {e}", exc_info=True)
    
    def start(self):
        """Start the multi-agent application"""
        logger.info("=" * 70)
        logger.info("🚀 Starting Mental Wellness Multi-Agent System")
        logger.info("=" * 70)
        
        try:
            # Start scheduler
            logger.info("Starting wellness scheduler...")
            self.scheduler.start()
            logger.info("✓ Scheduler running")

            logger.info("=" * 70)
            logger.info("✅ System is now ACTIVE and monitoring for users")
            logger.info("=" * 70)
            logger.info("")
            logger.info("Active Components:")
            logger.info("  • Analysis Agent (Gemini 2.0 Flash Thinking)")
            logger.info("  • Messaging Agent (Gemini 2.0 Flash)")
            logger.info("  • Telegram Bot")
            logger.info(f"  • Google Calendar: {'✓' if self.calendar_server else '✗'}")
            logger.info(f"  • Spotify: {'✓' if self.spotify_server else '✗'}")
            logger.info("  • Vertex AI Memory Store")
            logger.info("  • Task Scheduler")
            logger.info("")
            logger.info("Press Ctrl+C to stop the system")
            logger.info("=" * 70)

            # Start Telegram bot
            logger.info("Starting Telegram bot...")
            self.telegram_server.start()
            logger.info("✓ Telegram bot running")
            
        except Exception as e:
            logger.error(f"✗ Failed to start system: {e}", exc_info=True)
            raise
    
    def shutdown(self):
        """Gracefully shutdown the multi-agent application"""
        logger.info("=" * 70)
        logger.info("🛑 Shutting down Mental Wellness Multi-Agent System")
        logger.info("=" * 70)
        
        try:
            # Stop scheduler
            logger.info("Stopping scheduler...")
            self.scheduler.stop()
            logger.info("✓ Scheduler stopped")
            
            # Stop Telegram bot
            logger.info("Stopping Telegram bot...")
            self.telegram_server.stop()
            logger.info("✓ Telegram bot stopped")
            
            logger.info("=" * 70)
            logger.info("✅ System shutdown complete")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"✗ Error during shutdown: {e}", exc_info=True)


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description="Mental Wellness Multi-Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Multi-Agent Architecture:
  • Analysis Agent: Emotional analysis, wellness planning, resource coordination
  • Messaging Agent: Communication, check-ins, crisis detection
  
Communication: Telegram only
Memory: Google Vertex AI Memory Store
        """
    )
    
    args = parser.parse_args()
    
    # Create and start application
    try:
        app = MentalWellnessApp()
        app.start()
        
        # Keep running until interrupted
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("\n⚠ Keyboard interrupt received")
        app.shutdown()
    except Exception as e:
        logger.error(f"✗ Critical application error: {e}", exc_info=True)
        if 'app' in locals():
            app.shutdown()
        sys.exit(1)


if __name__ == "__main__":
    main()
