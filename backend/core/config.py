import os
from dotenv import load_dotenv

load_dotenv(override=True)

AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
FREE_DAILY_LIMIT = int(os.getenv("FREE_DAILY_LIMIT", "5"))

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8000/spotify/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
_cors_origins = os.getenv("CORS_ORIGINS")
CORS_ORIGINS = list(
    dict.fromkeys(
        origin.strip().rstrip("/")
        for origin in (
            _cors_origins.split(",")
            if _cors_origins
            else [FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"]
        )
        if origin.strip()
    )
)

JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_ACCESS_TTL_SECONDS = int(os.getenv("JWT_ACCESS_TTL_SECONDS", "900"))
JWT_REFRESH_TTL_SECONDS = int(os.getenv("JWT_REFRESH_TTL_SECONDS", "2592000"))
