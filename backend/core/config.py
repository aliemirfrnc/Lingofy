import base64
import hashlib
import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

AI_PROVIDER = os.getenv("AI_PROVIDER", "openrouter")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "qwen/qwen-2.5-coder-32b-instruct")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "http://localhost:3000")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "Lingofy")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

DATABASE_PATH = os.getenv("DATABASE_PATH", str(Path(__file__).resolve().parent.parent / "data" / "lingofy.db"))
DATABASE_URL = os.getenv("DATABASE_URL", "")
JWT_SECRET = os.getenv("JWT_SECRET", "")
COOKIE_SECRET = os.getenv("COOKIE_SECRET", "")
SPOTIFY_TOKEN_ENCRYPTION_KEY = os.getenv("SPOTIFY_TOKEN_ENCRYPTION_KEY", "")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8000/spotify/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")
_cors_origins = os.getenv("CORS_ORIGINS")
CORS_ORIGINS = list(dict.fromkeys(origin.strip().rstrip("/") for origin in (_cors_origins.split(",") if _cors_origins else [FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"]) if origin.strip()))

JWT_ACCESS_TTL_SECONDS = int(os.getenv("JWT_ACCESS_TTL_SECONDS", "900"))
JWT_REFRESH_TTL_SECONDS = int(os.getenv("JWT_REFRESH_TTL_SECONDS", "2592000"))
FREE_DAILY_LIMIT = int(os.getenv("FREE_DAILY_LIMIT", "5"))
OPENROUTER_TIMEOUT = float(os.getenv("OPENROUTER_TIMEOUT", "60.0"))
GROQ_TIMEOUT = float(os.getenv("GROQ_TIMEOUT", "30.0"))
DICTIONARY_TIMEOUT = float(os.getenv("DICTIONARY_TIMEOUT", "5.0"))
DB_TIMEOUT = float(os.getenv("DB_TIMEOUT", "15.0"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "604800"))
MAX_CACHE_SIZE = int(os.getenv("MAX_CACHE_SIZE", "1000"))

def get_spotify_token_encryption_key() -> bytes:
    """Return the dedicated production key or a deterministic local-development key."""
    if SPOTIFY_TOKEN_ENCRYPTION_KEY:
        return SPOTIFY_TOKEN_ENCRYPTION_KEY.encode("utf-8")
    # Local development must remain usable without persisting a random key.
    return base64.urlsafe_b64encode(hashlib.sha256((JWT_SECRET or "lingofy-local-dev").encode("utf-8")).digest())

def validate_configuration() -> None:
    """Validate deployment-critical settings at application startup, never at import time."""
    if not IS_PRODUCTION:
        return
    errors = []
    if DEBUG:
        errors.append("DEBUG=True is forbidden in production")
    if len(JWT_SECRET) < 32:
        errors.append("JWT_SECRET must be at least 32 characters")
    if len(COOKIE_SECRET) < 32:
        errors.append("COOKIE_SECRET must be at least 32 characters")
    if not SPOTIFY_TOKEN_ENCRYPTION_KEY:
        errors.append("SPOTIFY_TOKEN_ENCRYPTION_KEY is required")
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        errors.append("Spotify credentials are required")
    if not OPENROUTER_API_KEY or not GROQ_API_KEY:
        errors.append("OpenRouter and Groq credentials are required")
    if not FRONTEND_URL.startswith("https://"):
        errors.append("FRONTEND_URL must be an HTTPS URL")
    if "*" in CORS_ORIGINS:
        errors.append("CORS_ORIGINS cannot contain '*'")
    if not DATABASE_URL:
        errors.append("DATABASE_URL is required")
    if errors:
        raise RuntimeError("Invalid production configuration: " + "; ".join(errors))
