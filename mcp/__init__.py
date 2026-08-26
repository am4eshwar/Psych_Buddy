"""
MCP (Model Context Protocol) Server Integrations
"""
from mcp.telegram_server import TelegramMCPServer
from mcp.spotify_server import SpotifyMCPServer

__all__ = [
    'TelegramMCPServer',
    'SpotifyMCPServer',
]
