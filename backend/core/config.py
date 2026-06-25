import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

AI_PROVIDER = os.getenv("AI_PROVIDER", "openrouter")

# OpenRouter Config
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "qwen/qwen-2.5-coder-32b-instruct")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "http://localhost:3000")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "Lingofy")

# STT & Fast AI Config (Groq)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Startup Validation
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY .env dosyasında bulunamadı! OpenRouter çalışmayacak.")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY .env dosyasında bulunamadı! STT ve Groq çalışmayacak.")

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
