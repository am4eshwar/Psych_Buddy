"""
Configuration settings for Mental Wellness AI Agent
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Google AI Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

# Google Cloud / Vertex AI Configuration
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION", "us-central1")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "service-account.json")

# Set Google Application Credentials
if GOOGLE_CREDENTIALS_PATH:
    creds_path = Path(GOOGLE_CREDENTIALS_PATH)
    if not creds_path.is_absolute():
        creds_path = BASE_DIR / GOOGLE_CREDENTIALS_PATH
    
    if creds_path.exists():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(creds_path)

# Memory Configuration
MEMORY_RETENTION_DAYS = int(os.getenv("MEMORY_RETENTION_DAYS", "30"))

# Google Calendar API
GOOGLE_CALENDAR_CREDENTIALS_PATH = os.getenv(
    "GOOGLE_CALENDAR_CREDENTIALS_PATH",
    "credentials.json"
)
GOOGLE_CALENDAR_TOKEN_PATH = os.getenv(
    "GOOGLE_CALENDAR_TOKEN_PATH",
    "token.json"
)

# Telegram Bot (Only messaging platform)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Spotify API
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")

# Spotify Mood Playlists (Fallback/Default)
SPOTIFY_MOOD_PLAYLISTS = {
    "sadness": [
        {"name": "Comforting Piano", "uri": "spotify:playlist:37i9dQZF1DWSqBruwoIXkA", "url": "https://open.spotify.com/playlist/37i9dQZF1DWSqBruwoIXkA"},
        {"name": "Sad Songs", "uri": "spotify:playlist:37i9dQZF1DX7qK8ma5wgG1", "url": "https://open.spotify.com/playlist/37i9dQZF1DX7qK8ma5wgG1"},
    ],
    "anxiety": [
        {"name": "Calm Vibes", "uri": "spotify:playlist:37i9dQZF1DX1s9ktJ3899e", "url": "https://open.spotify.com/playlist/37i9dQZF1DX1s9ktJ3899e"},
        {"name": "Peaceful Piano", "uri": "spotify:playlist:37i9dQZF1DX4sWSpwq3LiO", "url": "https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO"},
    ],
    "anger": [
        {"name": "Calming Classical", "uri": "spotify:playlist:37i9dQZF1DWV7EzJMK2FUI", "url": "https://open.spotify.com/playlist/37i9dQZF1DWV7EzJMK2FUI"},
    ],
    "uplifting": [
        {"name": "Mood Booster", "uri": "spotify:playlist:37i9dQZF1DX3rxVfibe1L0", "url": "https://open.spotify.com/playlist/37i9dQZF1DX3rxVfibe1L0"},
        {"name": "Happy Hits", "uri": "spotify:playlist:37i9dQZF1DXdPec7aLTmlC", "url": "https://open.spotify.com/playlist/37i9dQZF1DXdPec7aLTmlC"},
    ]
}

# Application Settings
CHECK_IN_TIMES = os.getenv("CHECK_IN_TIMES", "09:00,13:00,17:00,21:00").split(",")
PROGRAM_DURATION_DAYS = int(os.getenv("PROGRAM_DURATION_DAYS", "7"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def validate_config():
    """Validate required configuration"""
    required_vars = {
        "GOOGLE_API_KEY": GOOGLE_API_KEY,
        "GOOGLE_PROJECT_ID": GOOGLE_PROJECT_ID,
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    }
    
    missing = [key for key, value in required_vars.items() if not value]
    
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Please check your .env file."
        )
