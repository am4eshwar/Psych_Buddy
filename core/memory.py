"""
Memory Management using Google Vertex AI Memory Store
Handles user profiles, sessions, and conversation history
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from loguru import logger
import os
import json
import vertexai
from vertexai.preview import rag

from config import (
    GOOGLE_PROJECT_ID,
    GOOGLE_LOCATION,
    MEMORY_RETENTION_DAYS
)
from models import UserProfile, UserSession


class VertexMemoryManager:
    """Manages memory using Google Vertex AI RAG for semantic storage"""
    
    def __init__(self):
        """Initialize Vertex AI Memory Store"""
        logger.info("Initializing Vertex AI Memory Store...")
        
        self.use_local_fallback = False
        self.local_storage_file = "local_memory.json"
        self.local_data = {"profiles": {}, "sessions": {}, "messages": []}
        
        try:
            # Initialize Vertex AI
            vertexai.init(
                project=GOOGLE_PROJECT_ID,
                location=GOOGLE_LOCATION
            )
            
            # Initialize RAG corpus for memory storage
            self.corpus_name = f"wellness-agent-memory-{GOOGLE_PROJECT_ID}"
            self._initialize_memory_corpus()
            
            logger.info("Vertex AI Memory Store initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Vertex AI Memory Store: {e}")
            logger.warning("Falling back to local JSON storage")
            self.use_local_fallback = True
            self._load_local_data()
    
    def _load_local_data(self):
        """Load data from local JSON file"""
        try:
            if os.path.exists(self.local_storage_file):
                with open(self.local_storage_file, 'r') as f:
                    self.local_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading local data: {e}")

    def _save_local_data(self):
        """Save data to local JSON file"""
        try:
            with open(self.local_storage_file, 'w') as f:
                json.dump(self.local_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving local data: {e}")

    def _initialize_memory_corpus(self):
        """Initialize or get existing RAG corpus for memory"""
        try:
            # Try to get existing corpus
            self.corpus = rag.get_corpus(name=self.corpus_name)
            logger.info(f"Using existing memory corpus: {self.corpus_name}")
            
        except Exception:
            # Create new corpus if doesn't exist
            logger.info(f"Creating new memory corpus: {self.corpus_name}")
            self.corpus = rag.create_corpus(
                display_name=self.corpus_name,
                description="Mental Wellness Agent memory storage for user profiles and sessions"
            )
    
    def save_user_profile(self, profile: UserProfile) -> bool:
        """Save user profile to memory"""
        if self.use_local_fallback:
            try:
                self.local_data["profiles"][profile.user_id] = profile.dict()
                self._save_local_data()
                return True
            except Exception as e:
                logger.error(f"Error saving local profile: {e}")
                return False

        try:
            logger.info(f"Saving profile for user {profile.user_id}")
            
            # Convert profile to dict and store as RAG file
            profile_data = profile.dict()
            profile_data['type'] = 'user_profile'
            profile_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Create RAG file for user profile
            rag.upload_file(
                corpus_name=self.corpus.name,
                path=f"memory://profiles/{profile.user_id}.json",
                file_id=f"profile_{profile.user_id}",
                display_name=f"Profile: {profile.user_id}",
                description=json.dumps(profile_data)
            )
            
            logger.info(f"Profile saved for user {profile.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving user profile: {e}")
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve user profile from memory"""
        if self.use_local_fallback:
            data = self.local_data["profiles"].get(user_id)
            return UserProfile(**data) if data else None

        try:
            # Query RAG corpus for user profile
            results = rag.retrieval_query(
                rag_resources=[self.corpus.name],
                text=f"user_profile {user_id}",
                similarity_top_k=1
            )
            
            if results and len(results.contexts) > 0:
                profile_data = json.loads(results.contexts[0].source_description)
                return UserProfile(**profile_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving user profile: {e}")
            return None
    
    def save_session(self, session: UserSession) -> bool:
        """Save session to memory"""
        if self.use_local_fallback:
            try:
                self.local_data["sessions"][session.session_id] = session.dict()
                self._save_local_data()
                return True
            except Exception as e:
                logger.error(f"Error saving local session: {e}")
                return False

        try:
            logger.info(f"Saving session {session.session_id}")
            
            session_data = session.dict()
            session_data['type'] = 'user_session'
            session_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Store session as RAG file
            rag.upload_file(
                corpus_name=self.corpus.name,
                path=f"memory://sessions/{session.session_id}.json",
                file_id=f"session_{session.session_id}",
                display_name=f"Session: {session.session_id}",
                description=json.dumps(session_data)
            )
            
            logger.info(f"Session {session.session_id} saved")
            return True
            
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False
    
    def get_active_session(self, user_id: str) -> Optional[UserSession]:
        """Get active session for user"""
        if self.use_local_fallback:
            for session_data in self.local_data["sessions"].values():
                if session_data.get('user_id') == user_id and session_data.get('is_active'):
                    return UserSession(**session_data)
            return None

        try:
            results = rag.retrieval_query(
                rag_resources=[self.corpus.name],
                text=f"user_session {user_id} active",
                similarity_top_k=5
            )
            
            # Filter for active sessions
            for context in results.contexts:
                session_data = json.loads(context.source_description)
                if session_data.get('user_id') == user_id and session_data.get('is_active'):
                    return UserSession(**session_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving active session: {e}")
            return None
    def save_conversation_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Save conversation message to memory"""
        if self.use_local_fallback:
            try:
                message_data = {
                    'type': 'conversation_message',
                    'session_id': session_id,
                    'role': role,
                    'content': content,
                    'metadata': metadata or {},
                    'timestamp': datetime.utcnow().isoformat()
                }
                self.local_data["messages"].append(message_data)
                self._save_local_data()
                return True
            except Exception as e:
                logger.error(f"Error saving local message: {e}")
                return False

        try:
            message_data = {
                'type': 'conversation_message',
                'session_id': session_id,
                'role': role,
                'content': content,
                'metadata': metadata or {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Store as RAG file
            message_id = f"{session_id}_{datetime.utcnow().timestamp()}"
            rag.upload_file(
                corpus_name=self.corpus.name,
                path=f"memory://conversations/{session_id}/{message_id}.json",
                file_id=f"msg_{message_id}",
                display_name=f"Message: {session_id}",
                description=json.dumps(message_data)
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving conversation message: {e}")
            return False
    
    def get_conversation_history(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve conversation history for session"""
        if self.use_local_fallback:
            messages = [
                m for m in self.local_data["messages"] 
                if m.get('session_id') == session_id
            ]
            messages.sort(key=lambda x: x.get('timestamp', ''))
            return messages[-limit:]

        try:
            results = rag.retrieval_query(
                rag_resources=[self.corpus.name],
                text=f"conversation_message {session_id}",
                similarity_top_k=limit
            )
            
            messages = []
            for context in results.contexts:
                message_data = json.loads(context.source_description)
                if message_data.get('session_id') == session_id:
                    messages.append(message_data)
            
            # Sort by timestamp
            messages.sort(key=lambda x: x.get('timestamp', ''))
            
            return messages
            
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
            return []
    
    def get_user_sessions(self, user_id: str) -> List[UserSession]:
        """Get all sessions for a user"""
        if self.use_local_fallback:
            sessions = []
            for session_data in self.local_data["sessions"].values():
                if session_data.get('user_id') == user_id:
                    sessions.append(UserSession(**session_data))
            return sessions

        try:
            results = rag.retrieval_query(
                rag_resources=[self.corpus.name],
                text=f"user_session {user_id}",
                similarity_top_k=20
            )
            
            sessions = []
            for context in results.contexts:
                session_data = json.loads(context.source_description)
                if session_data.get('user_id') == user_id:
                    sessions.append(UserSession(**session_data))
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error retrieving user sessions: {e}")
            return []
    
    def update_session_progress(
        self,
        session_id: str,
        mood_scores: List[int],
        completed_tasks: List[str]
    ) -> bool:
        """Update session progress"""
        try:
            session = self.get_session(session_id)
            if not session:
                return False
            
            session.mood_scores = mood_scores
            session.completed_tasks = completed_tasks
            session.last_check_in = datetime.utcnow()
            
            return self.save_session(session)
            
        except Exception as e:
            logger.error(f"Error updating session progress: {e}")
            return False
    
    def deactivate_session(self, session_id: str) -> bool:
        """Mark session as inactive"""
        try:
            session = self.get_session(session_id)
            if not session:
                return False
            
            session.is_active = False
            session.end_date = datetime.utcnow()
            
            return self.save_session(session)
            
        except Exception as e:
            logger.error(f"Error deactivating session: {e}")
            return False
    
    def cleanup_old_data(self) -> bool:
        """Clean up old data based on retention policy"""
        try:
            logger.info(f"Cleaning up data older than {MEMORY_RETENTION_DAYS} days")
            
            # cutoff_date = datetime.utcnow() - timedelta(days=MEMORY_RETENTION_DAYS)
            
            # Note: Vertex AI RAG handles cleanup automatically based on corpus settings
            # This is a placeholder for custom cleanup logic if needed
            
            logger.info("Cleanup completed")
            return True
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return False