"""
Agent Orchestrator - Core ReAct Engine
Coordinates interactions using Google Gemini and automated tool calling.
"""
from typing import Dict, Any, Optional
import asyncio
from loguru import logger
from datetime import datetime

import google.generativeai as genai
from google.generativeai.types import content_types

from config import GOOGLE_API_KEY, GEMINI_MODEL
from core.tools.memory_tools import get_memory_tools
from core.tools.wellness_tools import get_wellness_tools
from core.tools.therapeutic_tools import get_therapeutic_tools


class AgentOrchestrator:
    """
    Orchestrates the ReAct loop for the Psych Buddy agent.
    """
    
    def __init__(
        self,
        memory_manager,
        telegram_server,
        spotify_server=None,
        scheduler=None
    ):
        """Initialize orchestrator with tools and lock manager."""
        logger.info("Initializing Agent Orchestrator ReAct Engine...")
        
        self.memory = memory_manager
        self.telegram = telegram_server
        self.spotify = spotify_server
        self.scheduler = scheduler
        
        # Concurrency locks per user
        self._user_locks: Dict[str, asyncio.Lock] = {}
        
        # Configure Gemini
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # System instructions
        self.base_system_instruction = (
            "You are an autonomous psychological support agent called Psych Buddy. "
            "You are designed to provide empathetic, evidence-based mental wellness support. "
            "You have access to several tools. You must reason about the user's state, "
            "use tools to gather context or perform actions, and finally respond to the user. "
            "If the user is new, you MUST use the schedule_program tool to set up their check-ins. "
            "Be concise, compassionate, and therapeutic. "
            "Never ignore self-harm or suicidal intent; always trigger_crisis_protocol immediately."
        )
        
        logger.info("Agent Orchestrator initialized with ReAct capabilities")

    def _get_user_lock(self, user_id: str) -> asyncio.Lock:
        if user_id not in self._user_locks:
            self._user_locks[user_id] = asyncio.Lock()
        return self._user_locks[user_id]

    async def run_react_loop(
        self, user_id: str, message: str, context_type: str = "chat"
    ) -> str:
        """
        Main execution loop for processing user input or system triggers.
        Utilizes a lock to prevent race conditions on double-texts.
        """
        async with self._get_user_lock(user_id):
            logger.info(f"Starting ReAct loop for user {user_id} (context: {context_type})")
            
            try:
                # 1. Gather context for the system prompt
                active_session = await self.memory.get_active_session(user_id)
                session_summary = "No active session."
                if active_session:
                    session_summary = (
                        f"Active Session: state={getattr(active_session, 'session_state', 'unknown')}, "
                        f"primary_state={active_session.primary_mental_state}, "
                        f"intensity={active_session.intensity}"
                    )
                
                # Fetch summary of recent messages to inject into system prompt
                context = await self.memory.get_context_for_turn(user_id, message)
                recent_history = "\n".join([
                    f"{m.get('role', 'unknown')}: {m.get('content', '')}" 
                    for m in context.get("messages", [])[-5:]
                ])
                
                system_instruction = (
                    f"{self.base_system_instruction}\n\n"
                    f"USER ID: {user_id}\n"
                    f"SESSION CONTEXT: {session_summary}\n\n"
                    f"RECENT CONVERSATION HISTORY (for context):\n{recent_history}\n\n"
                )
                
                # Prepend context context_type hint if it's a system trigger
                final_message = message
                if context_type == "check_in":
                    system_instruction += "\nCONTEXT: You are proactively checking in on the user. The user has not sent a message, this is a system trigger."
                    final_message = f"SYSTEM NOTIFICATION: {message}"
                elif context_type == "task_reminder":
                    system_instruction += "\nCONTEXT: You are reminding the user about a scheduled wellness task. Ask them if they completed it."
                    final_message = f"SYSTEM NOTIFICATION: {message}"

                # 2. Assemble tools
                memory_tools = get_memory_tools(self.memory, user_id)
                wellness_tools = get_wellness_tools(self.memory, user_id, self.scheduler)
                therapeutic_tools = get_therapeutic_tools(self.memory, user_id, self.spotify)
                
                all_tools = memory_tools + wellness_tools + therapeutic_tools
                
                # 3. Initialize Model
                model = genai.GenerativeModel(
                    model_name=GEMINI_MODEL,
                    system_instruction=system_instruction,
                    tools=all_tools,
                    generation_config={
                        'temperature': 0.7,
                    }
                )
                
                # 4. Start Chat (Empty history, rely on injected context)
                # DO NOT use enable_automatic_function_calling=True because tools are async
                chat = model.start_chat()
                
                # 5. Execute ReAct Loop manually
                logger.debug(f"Sending message to Gemini for user {user_id}: {final_message[:50]}...")
                response = await chat.send_message_async(final_message)
                
                # Manual tool calling loop
                max_iterations = 10
                for _ in range(max_iterations):
                    if not response.parts or not response.parts[0].function_call:
                        break
                        
                    part = response.parts[0]
                    func_call = part.function_call
                    func_name = func_call.name
                    logger.info(f"Model calling tool: {func_name}")
                    
                    # Find tool
                    func = next((t for t in all_tools if t.__name__ == func_name), None)
                    if func:
                        try:
                            # Convert protobuf MapComposite to dict
                            args = {k: v for k, v in func_call.args.items()}
                            # Execute the async tool
                            result = await func(**args)
                        except Exception as e:
                            logger.error(f"Error executing tool {func_name}: {e}")
                            result = f"Error: {str(e)}"
                    else:
                        result = "Error: Function not found"
                        
                    # Format response
                    func_response = [{
                        "function_response": {
                            "name": func_name,
                            "response": {"result": result}
                        }
                    }]
                    # Send tool result back
                    response = await chat.send_message_async(func_response)
                
                logger.info(f"ReAct loop completed for user {user_id}")
                return response.text
                
            except Exception as e:
                logger.error(f"Error in run_react_loop for user {user_id}: {e}", exc_info=True)
                return "I apologize, but I encountered an error while processing that. Please try again."