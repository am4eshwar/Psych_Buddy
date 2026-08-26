"""
Memory and State tools for the ReAct architecture.
Provides functions with clear schemas for the LLM to call autonomously.
"""
from typing import Dict, Any, List
import asyncio
from loguru import logger

def get_memory_tools(memory_manager, user_id: str):
    """
    Factory function to return memory and state tools bound to the current user
    and memory manager. These functions expose clear schemas for the LLM.
    """

    async def search_past_conversations(query: str) -> List[Dict[str, Any]]:
        """
        Queries the user's past memories (Mem0/Qdrant).
        Call this if the user references something from the past that you need to recall.
        
        Args:
            query: The search query to find relevant past conversations or facts.
        """
        logger.info(f"LLM Tool Call: search_past_conversations for {user_id}")
        memories = await memory_manager.retrieve_memories(user_id, query)
        return memories

    async def save_important_fact(fact: str, category: str) -> str:
        """
        Writes a specific important fact about the user to long-term memory.
        Call this when you learn something new and important (e.g., "User's dog died last week").
        
        Args:
            fact: The specific fact or event to remember.
            category: The category of the fact (e.g., 'personal', 'medical', 'event').
        """
        logger.info(f"LLM Tool Call: save_important_fact for {user_id}")
        metadata = {"category": category, "source": "agent_deduction"}
        await memory_manager.add_memory(user_id, fact, metadata=metadata)
        return "Fact successfully saved to long-term memory."

    async def get_user_profile() -> Dict[str, Any]:
        """
        Fetches the user's demographics, timezone, and current session state from the database.
        Call this to understand who the user is and their current state before formulating a plan.
        """
        logger.info(f"LLM Tool Call: get_user_profile for {user_id}")
        profile = await memory_manager.get_user_profile(user_id)
        session = await memory_manager.get_active_session(user_id)
        
        return {
            "profile": profile.model_dump() if profile else None,
            "session": session.model_dump() if session else None
        }

    async def update_session_state(state: str) -> str:
        """
        Updates the user's current session state.
        Allows the agent to mark the user as "in_crisis", "awaiting_check_in", or "stable".
        
        Args:
            state: The new state of the user. Must be "in_crisis", "awaiting_check_in", or "stable".
        """
        logger.info(f"LLM Tool Call: update_session_state to {state} for {user_id}")
        session = await memory_manager.get_active_session(user_id)
        if session:
            session.session_state = state
            if state == "in_crisis":
                session.requires_professional_help = True
            await memory_manager.save_session(session)
            return f"Session state successfully updated to {state}."
        return "Failed to update state: No active session found."

    return [
        search_past_conversations,
        save_important_fact,
        get_user_profile,
        update_session_state
    ]
