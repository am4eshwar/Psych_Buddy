"""
Configuration settings for Psych Buddy
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
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ═══════════════════════════════════════════════════════════════
# Memory Architecture Configuration
# ═══════════════════════════════════════════════════════════════

# --- Redis (Short-term session context) ---
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_SESSION_TTL = int(os.getenv("REDIS_SESSION_TTL", "3600"))  # 1 hour default

# --- PostgreSQL (Task & schedule persistence) ---
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/psych_agent")
POSTGRES_SYNC_URL = os.getenv(
    "POSTGRES_SYNC_URL",
    "postgresql://postgres:postgres@localhost:5432/psych_agent"
)

# --- Qdrant (Vector store for Mem0) ---
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_URL = os.getenv("QDRANT_URL", None)  # Use full URL for hosted Qdrant (overrides host/port)
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)  # Required for hosted Qdrant
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "wellness_memories")

# --- Mem0 (Episodic & semantic memory) ---
MEM0_LLM_MODEL = os.getenv("MEM0_LLM_MODEL", f"gemini/{GEMINI_MODEL}")
MEM0_EMBEDDER_MODEL = os.getenv(
    "MEM0_EMBEDDER_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)
MEM0_EMBEDDING_DIMS = int(os.getenv("MEM0_EMBEDDING_DIMS", "384"))
MEM0_TOP_K = int(os.getenv("MEM0_TOP_K", "5"))

# Memory retention
MEMORY_RETENTION_DAYS = int(os.getenv("MEMORY_RETENTION_DAYS", "30"))

# Build Mem0 config dict (consumed by Memory.from_config)
def get_mem0_config() -> dict:
    """Build Mem0 configuration dictionary."""
    vector_store_config = {
        "collection_name": QDRANT_COLLECTION_NAME,
        "embedding_model_dims": MEM0_EMBEDDING_DIMS,
    }

    # Support both local and hosted Qdrant
    if QDRANT_URL:
        vector_store_config["url"] = QDRANT_URL
        if QDRANT_API_KEY:
            vector_store_config["api_key"] = QDRANT_API_KEY
    else:
        vector_store_config["host"] = QDRANT_HOST
        vector_store_config["port"] = QDRANT_PORT

    return {
        "llm": {
            "provider": "litellm",
            "config": {
                "model": MEM0_LLM_MODEL,
                "temperature": 0.1,
                "max_tokens": 2000,
            },
        },
        "embedder": {
            "provider": "huggingface",
            "config": {
                "model": MEM0_EMBEDDER_MODEL,
                "embedding_dims": MEM0_EMBEDDING_DIMS,
            },
        },
        "vector_store": {
            "provider": "qdrant",
            "config": vector_store_config,
        },
    }

# ═══════════════════════════════════════════════════════════════
# Google Calendar API (Optional)
# ═══════════════════════════════════════════════════════════════
GOOGLE_CALENDAR_CREDENTIALS_PATH = os.getenv(
    "GOOGLE_CALENDAR_CREDENTIALS_PATH",
    "credentials.json"
)
GOOGLE_CALENDAR_TOKEN_PATH = os.getenv(
    "GOOGLE_CALENDAR_TOKEN_PATH",
    "token.json"
)

# ═══════════════════════════════════════════════════════════════
# Telegram Bot (Only messaging platform)
# ═══════════════════════════════════════════════════════════════
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ═══════════════════════════════════════════════════════════════
# Spotify API (Optional)
# ═══════════════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════════════
# Application Settings
# ═══════════════════════════════════════════════════════════════
CHECK_IN_TIMES = os.getenv("CHECK_IN_TIMES", "09:00,13:00,17:00,21:00").split(",")
PROGRAM_DURATION_DAYS = int(os.getenv("PROGRAM_DURATION_DAYS", "7"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Consolidation settings
CONSOLIDATION_INTERVAL_TURNS = int(os.getenv("CONSOLIDATION_INTERVAL_TURNS", "10"))


def validate_config():
    """Validate required configuration"""
    required_vars = {
        "GOOGLE_API_KEY": GOOGLE_API_KEY,
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    }
    
    missing = [key for key, value in required_vars.items() if not value]
    
    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Please check your .env file."
        )
