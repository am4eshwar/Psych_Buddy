"""
Telegram Bot MCP Server for messaging integration
"""
from typing import Optional
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from loguru import logger

from config import TELEGRAM_BOT_TOKEN


class TelegramMCPServer:
    """MCP Server for Telegram messaging"""
    
    def __init__(self, bot_token: Optional[str] = None):
        """Initialize Telegram bot"""
        self.bot_token = bot_token or TELEGRAM_BOT_TOKEN
        if not self.bot_token:
            raise ValueError("Telegram bot token not provided")
        
        self.app = Application.builder().token(self.bot_token).build()
        self.message_callback = None
        self.bot = Bot(self.bot_token)
        
        logger.info("Telegram MCP Server initialized")
    
    def register_message_handler(self, callback):
        """Register callback for incoming messages"""
        self.message_callback = callback
        logger.info("Message callback registered")
    
    async def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: Optional[str] = "Markdown"
    ) -> bool:
        """
        Send message to user
        
        Args:
            chat_id: Telegram chat ID
            text: Message text
            parse_mode: Text formatting mode
            
        Returns:
            Success status
        """
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode
            )
            logger.info(f"Sent message to {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    async def send_check_in(
        self,
        chat_id: str,
        questions: str,
        session_id: str
    ) -> bool:
        """Send check-in questions"""
        message = f"🌟 **Check-in Time!**\n\n{questions}\n\n_Session: {session_id[:8]}_"
        return await self.send_message(chat_id, message)
    
    async def send_task_reminder(
        self,
        chat_id: str,
        task_title: str,
        task_description: str,
        scheduled_time: str
    ) -> bool:
        """Send task reminder"""
        message = f"""⏰ **Task Reminder**

📝 {task_title}

{task_description}

Scheduled for: {scheduled_time}"""
        return await self.send_message(chat_id, message)
    
    async def send_wellness_plan(
        self,
        chat_id: str,
        plan_summary: str
    ) -> bool:
        """Send wellness plan summary"""
        message = f"""🌈 **Your Personalized Wellness Plan**

{plan_summary}

I'll be checking in with you 4 times daily to support your journey. You've got this! 💪"""
        return await self.send_message(chat_id, message)
    
    async def send_encouragement(
        self,
        chat_id: str,
        message_text: str
    ) -> bool:
        """Send encouragement message"""
        message = f"💙 {message_text}"
        return await self.send_message(chat_id, message)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        if self.message_callback and update.message:
            chat_id = str(update.effective_chat.id)
            user_message = update.message.text
            
            # Call the registered callback
            try:
                response = await self.message_callback(chat_id, user_message)
                if response:
                    await update.message.reply_text(response)
            except Exception as e:
                logger.error(f"Error in message callback: {e}")
                await update.message.reply_text(
                    "I'm having trouble processing that right now. Please try again in a moment."
                )
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """👋 Welcome to Psych Buddy!

I'm here to support you on your wellness journey. Share how you're feeling, and I'll help create a personalized plan to support you.

Just send me a message describing your current emotional state and what you're going through."""
        
        await update.message.reply_text(welcome_message)
    
    def setup_handlers(self):
        """Setup message handlers"""
        self.app.add_handler(CommandHandler("start", self.handle_start))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    def start(self):
        """Start the bot (blocking)"""
        self.setup_handlers()
        logger.info("Starting Telegram bot...")
        self.app.run_polling()
    
    async def start_async(self):
        """Start the bot (async)"""
        self.setup_handlers()
        logger.info("Starting Telegram bot (async)...")
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
    
    async def stop(self):
        """Stop the bot"""
        if self.app.running:
            await self.app.stop()
            logger.info("Telegram bot stopped")
