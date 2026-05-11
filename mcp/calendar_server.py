"""
Google Calendar MCP Server for task scheduling
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from loguru import logger

from config import GOOGLE_CALENDAR_CREDENTIALS_PATH, GOOGLE_CALENDAR_TOKEN_PATH


class GoogleCalendarMCPServer:
    """MCP Server for Google Calendar integration"""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        """Initialize Google Calendar API"""
        self.creds = None
        self.service = None
        self._authenticate()
        logger.info("Google Calendar MCP Server initialized")
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        # Load existing credentials
        if os.path.exists(GOOGLE_CALENDAR_TOKEN_PATH):
            self.creds = Credentials.from_authorized_user_file(
                GOOGLE_CALENDAR_TOKEN_PATH,
                self.SCOPES
            )
        
        # If no valid credentials, get new ones
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except (RefreshError, Exception) as e:
                    logger.warning(f"Failed to refresh token: {e}. Re-authenticating...")
                    self.creds = None

            if not self.creds:
                flow = InstalledAppFlow.from_client_secrets_file(
                    GOOGLE_CALENDAR_CREDENTIALS_PATH,
                    self.SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(GOOGLE_CALENDAR_TOKEN_PATH, 'w') as token:
                token.write(self.creds.to_json())
        
        # Build service
        self.service = build('calendar', 'v3', credentials=self.creds)
        logger.info("Authenticated with Google Calendar")
    
    def create_event(
        self,
        summary: str,
        description: str,
        start_time: datetime,
        duration_minutes: int,
        reminders: Optional[List[int]] = None
    ) -> Optional[str]:
        """
        Create a calendar event
        
        Args:
            summary: Event title
            description: Event description
            start_time: Start datetime
            duration_minutes: Duration in minutes
            reminders: List of reminder times in minutes before event
            
        Returns:
            Event ID if successful
        """
        try:
            end_time = start_time + timedelta(minutes=duration_minutes)
            
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': mins}
                        for mins in (reminders or [10])
                    ],
                },
            }
            
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            event_id = created_event.get('id')
            logger.info(f"Created calendar event: {event_id}")
            return event_id
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            return None
    
    def create_wellness_task(
        self,
        task_title: str,
        task_description: str,
        scheduled_time: datetime,
        duration_minutes: int = 15
    ) -> Optional[str]:
        """Create a wellness task event"""
        return self.create_event(
            summary=f"🧘 {task_title}",
            description=f"Wellness Activity:\n\n{task_description}",
            start_time=scheduled_time,
            duration_minutes=duration_minutes,
            reminders=[5, 15]  # 5 and 15 minutes before
        )
    
    def create_check_in_event(
        self,
        session_id: str,
        check_in_time: datetime,
        check_in_type: str
    ) -> Optional[str]:
        """Create a check-in event"""
        return self.create_event(
            summary=f"💙 Wellness Check-in ({check_in_type})",
            description=f"Time for your {check_in_type} wellness check-in.\n\nSession: {session_id[:8]}",
            start_time=check_in_time,
            duration_minutes=10,
            reminders=[0, 5]  # At event time and 5 min before
        )
    
    def create_program_schedule(
        self,
        session_id: str,
        tasks: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Create full program schedule
        
        Args:
            session_id: Session identifier
            tasks: List of task dictionaries with title, description, time, duration
            
        Returns:
            List of created event IDs
        """
        event_ids = []
        
        for task in tasks:
            event_id = self.create_wellness_task(
                task_title=task.get('title', 'Wellness Activity'),
                task_description=task.get('description', ''),
                scheduled_time=task.get('scheduled_time', datetime.now()),
                duration_minutes=task.get('duration_minutes', 15)
            )
            
            if event_id:
                event_ids.append(event_id)
        
        logger.info(f"Created {len(event_ids)} calendar events for session {session_id}")
        return event_ids
    
    def update_event(
        self,
        event_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update an existing event"""
        try:
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Apply updates
            for key, value in updates.items():
                event[key] = value
            
            self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"Updated event: {event_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Error updating event: {e}")
            return False
    
    def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event"""
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            logger.info(f"Deleted event: {event_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Error deleting event: {e}")
            return False
    
    def get_upcoming_events(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get upcoming calendar events"""
        try:
            now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return events
            
        except HttpError as e:
            logger.error(f"Error getting events: {e}")
            return []
