"""
Therapeutic tools for the ReAct architecture.
Provides functions for mood tracking, music recommendations, and crisis management.
"""
from typing import Dict, Any, List
from loguru import logger
import json

from config.mental_states import MentalState, EMERGENCY_RESOURCES


def get_therapeutic_tools(memory_manager, user_id: str, spotify_server=None):
    """
    Factory function to return therapeutic tools bound to the current user,
    memory manager, and Spotify server.
    These functions expose clear schemas for the LLM.
    """

    async def get_music_recommendation(mood: str) -> Dict[str, Any]:
        """
        Calls the Spotify MCP server to recommend calming or mood-appropriate music.
        Call this if you reason the user needs a distraction, emotional processing, or calming sounds.
        
        Args:
            mood: The user's current mood or mental state (e.g., 'anxiety', 'sadness', 'anger', 'stress').
        """
        logger.info(f"LLM Tool Call: get_music_recommendation for {mood} ({user_id})")
        if not spotify_server:
            return {"error": "Spotify server is not configured or available."}
            
        try:
            # Try to map string to MentalState Enum
            try:
                mental_state = MentalState(mood.lower())
            except ValueError:
                # If exact match fails, use a fallback
                mental_state = MentalState.STRESS
                
            recommendations = spotify_server.get_wellness_recommendations(mental_state)
            return recommendations
        except Exception as e:
            logger.error(f"Error getting music recommendations: {e}")
            return {"error": str(e)}

    async def record_mood_score(score: int, energy: int) -> str:
        """
        Records the user's mood and energy metrics for progress tracking.
        Call this when you complete a check-in conversation and have gauged their current metrics.
        
        Args:
            score: The mood score from 1 (lowest) to 10 (highest).
            energy: The energy level from 1 (lowest) to 10 (highest).
        """
        logger.info(f"LLM Tool Call: record_mood_score (score={score}, energy={energy}) for {user_id}")
        session = await memory_manager.get_active_session(user_id)
        if not session:
            return "Failed to record mood score: No active session found."
            
        if not hasattr(session, 'mood_scores'):
            session.mood_scores = []
            
        session.mood_scores.append(score)
        
        # Optionally, save this as a direct fact in episodic memory
        fact = f"User reported mood score of {score}/10 and energy level of {energy}/10."
        metadata = {"category": "mood_tracking", "score": score, "energy": energy}
        await memory_manager.add_memory(user_id, fact, metadata=metadata)
        
        await memory_manager.save_session(session)
        return f"Successfully recorded mood score {score} and energy {energy}."

    async def trigger_crisis_protocol() -> Dict[str, Any]:
        """
        Immediately flags the user's session in the database as requiring professional help
        and returns emergency contact resources.
        Call this immediately if the user mentions self-harm, suicide, or severe crisis.
        """
        logger.info(f"LLM Tool Call: trigger_crisis_protocol for {user_id}")
        session = await memory_manager.get_active_session(user_id)
        if session:
            session.requires_professional_help = True
            session.session_state = "in_crisis"
            await memory_manager.save_session(session)
            
        # Log this critical event
        await memory_manager.add_memory(
            user_id, 
            "CRISIS PROTOCOL TRIGGERED: User indicated severe distress or self-harm risk.", 
            metadata={"category": "crisis_alert", "severity": "high"}
        )
            
        return {
            "status": "Crisis protocol activated. Session flagged for professional help.",
            "emergency_resources": EMERGENCY_RESOURCES,
            "instruction": "Please provide these resources to the user immediately in a compassionate tone."
        }

    return [
        get_music_recommendation,
        record_mood_score,
        trigger_crisis_protocol
    ]
