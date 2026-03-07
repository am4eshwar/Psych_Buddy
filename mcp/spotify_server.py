"""
Spotify MCP Server for mood-based music recommendations
"""
from typing import Optional, List, Dict, Any
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from loguru import logger

from config import (
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI,
    SPOTIFY_MOOD_PLAYLISTS
)
from config.mental_states import MentalState


class SpotifyMCPServer:
    """MCP Server for Spotify integration"""
    
    SCOPE = "playlist-read-private playlist-modify-public playlist-modify-private user-library-read"
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None
    ):
        """Initialize Spotify client"""
        self.client_id = client_id or SPOTIFY_CLIENT_ID
        self.client_secret = client_secret or SPOTIFY_CLIENT_SECRET
        self.redirect_uri = redirect_uri or SPOTIFY_REDIRECT_URI
        
        if not all([self.client_id, self.client_secret]):
            logger.warning("Spotify credentials not configured")
            self.sp = None
            return
        
        try:
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.SCOPE
            )
            
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            logger.info("Spotify MCP Server initialized")
        except Exception as e:
            logger.error(f"Error initializing Spotify: {e}")
            self.sp = None
    
    def get_mood_playlists(
        self,
        mental_state: MentalState,
        limit: int = 3
    ) -> List[Dict[str, str]]:
        """
        Get curated playlists for a mental state
        
        Args:
            mental_state: User's mental state
            limit: Number of playlists to return
            
        Returns:
            List of playlist info dictionaries
        """
        # Get predefined mood playlists
        state_key = mental_state.value
        
        # Check for specific state playlists
        if state_key in SPOTIFY_MOOD_PLAYLISTS:
            return SPOTIFY_MOOD_PLAYLISTS[state_key][:limit]
        
        # Default fallback playlists
        return SPOTIFY_MOOD_PLAYLISTS.get("uplifting", [])[:limit]
    
    def search_playlists(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for playlists by keyword
        
        Args:
            query: Search query
            limit: Number of results
            
        Returns:
            List of playlist info
        """
        if not self.sp:
            logger.warning("Spotify not configured")
            return []
        
        try:
            results = self.sp.search(q=query, type='playlist', limit=limit)
            playlists = results.get('playlists', {}).get('items', [])
            
            return [
                {
                    'name': pl['name'],
                    'uri': pl['uri'],
                    'url': pl['external_urls']['spotify'],
                    'description': pl.get('description', ''),
                    'owner': pl['owner']['display_name']
                }
                for pl in playlists
            ]
        except Exception as e:
            logger.error(f"Error searching Spotify playlists: {e}")
            return []
    
    def get_recommendations_by_mood(
        self,
        mood: str,
        energy: str = "medium"
    ) -> List[Dict[str, str]]:
        """
        Get playlist recommendations based on mood and energy level
        
        Args:
            mood: Emotional state (sad, happy, calm, energetic, etc.)
            energy: Energy level (low, medium, high)
            
        Returns:
            List of recommended playlists
        """
        # Mood to search query mapping
        mood_queries = {
            "sad": "sad songs, melancholy, emotional",
            "happy": "happy vibes, feel good, positive",
            "calm": "calm, peaceful, relaxation",
            "anxious": "anxiety relief, calm down, meditation",
            "angry": "release anger, intense, workout",
            "lonely": "comfort, companionship, soothing",
            "stressed": "stress relief, chill, ambient",
            "motivated": "motivation, uplifting, energetic"
        }
        
        # Energy level affects music selection
        energy_modifiers = {
            "low": "ambient, peaceful, gentle",
            "medium": "moderate tempo, balanced",
            "high": "upbeat, energetic, active"
        }
        
        query = mood_queries.get(mood.lower(), "wellness playlist")
        query += f" {energy_modifiers.get(energy.lower(), '')}"
        
        return self.search_playlists(query, limit=3)
    
    def get_wellness_recommendations(
        self,
        mental_state: MentalState,
        time_of_day: str = "any"
    ) -> Dict[str, Any]:
        """
        Get comprehensive music recommendations for wellness
        
        Args:
            mental_state: User's mental state
            time_of_day: Time of day (morning, afternoon, evening, night)
            
        Returns:
            Dictionary with recommendations and guidance
        """
        recommendations = {
            "mental_state": mental_state.value,
            "time_of_day": time_of_day,
            "playlists": [],
            "guidance": ""
        }
        
        # Get mood-appropriate playlists
        playlists = self.get_mood_playlists(mental_state)
        recommendations["playlists"] = playlists
        
        # Time-based guidance
        time_guidance = {
            "morning": "Start your day with uplifting music to set a positive tone.",
            "afternoon": "Use music to maintain energy and focus during the day.",
            "evening": "Transition to calmer music to help you wind down.",
            "night": "Choose peaceful, soothing music to prepare for rest."
        }
        
        # State-based guidance
        state_guidance = {
            MentalState.SADNESS: "It's okay to listen to sad music to process emotions, but also include some uplifting tracks.",
            MentalState.ANXIETY: "Focus on slow-tempo, instrumental music to help calm your nervous system.",
            MentalState.ANGER: "Start with intense music to release energy, then transition to calming sounds.",
            MentalState.LONELINESS: "Music can be a companion. Choose comforting, familiar songs.",
            MentalState.STRESS: "Ambient and nature sounds can help reduce stress hormones.",
        }
        
        guidance = state_guidance.get(mental_state, "Music can support your emotional well-being.")
        guidance += " " + time_guidance.get(time_of_day, "")
        
        recommendations["guidance"] = guidance
        
        return recommendations
    
    def create_custom_wellness_playlist(
        self,
        name: str,
        description: str,
        track_uris: List[str]
    ) -> Optional[str]:
        """
        Create a custom playlist for user
        
        Args:
            name: Playlist name
            description: Playlist description
            track_uris: List of Spotify track URIs
            
        Returns:
            Playlist URI if successful
        """
        if not self.sp:
            logger.warning("Spotify not configured")
            return None
        
        try:
            user_id = self.sp.current_user()['id']
            
            playlist = self.sp.user_playlist_create(
                user_id,
                name,
                public=False,
                description=description
            )
            
            if track_uris:
                self.sp.playlist_add_items(playlist['id'], track_uris)
            
            logger.info(f"Created custom playlist: {playlist['id']}")
            return playlist['uri']
            
        except Exception as e:
            logger.error(f"Error creating playlist: {e}")
            return None
    
    def get_playlist_url(self, playlist_uri: str) -> str:
        """Convert Spotify URI to web URL"""
        if playlist_uri.startswith("spotify:playlist:"):
            playlist_id = playlist_uri.split(":")[-1]
            return f"https://open.spotify.com/playlist/{playlist_id}"
        return playlist_uri
