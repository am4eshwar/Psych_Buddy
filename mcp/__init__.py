"""
MCP (Model Context Protocol) Server Integrations
"""
from mcp.telegram_server import TelegramMCPServer
from mcp.calendar_server import GoogleCalendarMCPServer
from mcp.spotify_server import SpotifyMCPServer

__all__ = [
    'TelegramMCPServer',
    'GoogleCalendarMCPServer',
    'SpotifyMCPServer',
]
