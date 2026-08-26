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
        spotify_server=None
    ):
        """Initialize orchestrator with both agents"""
        logger.info("Initializing Agent Orchestrator...")
        
        self.memory = memory_manager

        self.spotify = spotify_server
        
        # Initialize specialized agents
        self.analysis_agent = AnalysisAgent(memory_manager)
        self.messaging_agent = MessagingAgent(memory_manager, telegram_server)
        
        logger.info("Agent Orchestrator initialized with 2 specialized agents")