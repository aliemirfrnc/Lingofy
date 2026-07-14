import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT.lower() == "production"
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

DEBUG = os.getenv("DEBUG", "False").lower() == "true"
DATABASE_PATH = os.getenv("DATABASE_PATH", str(Path(__file__).resolve().parent.parent / "data" / "lingofy.db"))
JWT_SECRET = os.getenv("JWT_SECRET", "")
COOKIE_SECRET = os.getenv("COOKIE_SECRET", "")

if IS_PRODUCTION:
    if DEBUG:
        raise ValueError("Production ortamında DEBUG=True kullanılamaz!")
    if not JWT_SECRET or len(JWT_SECRET) < 32 or JWT_SECRET == "your_super_secret_jwt_key_here_at_least_32_chars":
        raise ValueError("Production ortamında güçlü bir JWT_SECRET (min 32 karakter) zorunludur.")
    if not COOKIE_SECRET or len(COOKIE_SECRET) < 32:
        raise ValueError("Production ortamında güçlü bir COOKIE_SECRET (min 32 karakter) zorunludur.")
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        raise ValueError("Production ortamında SPOTIFY_CLIENT_ID ve SPOTIFY_CLIENT_SECRET zorunludur.")
    if not FRONTEND_URL or "localhost" in FRONTEND_URL:
        raise ValueError("Production ortamında FRONTEND_URL geçerli bir domain olmalıdır.")

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

if IS_PRODUCTION and "*" in CORS_ORIGINS:
    raise ValueError("Production ortamında CORS_ORIGINS içinde '*' kullanılamaz! Güvenli domainler tanımlayın.")

JWT_ACCESS_TTL_SECONDS = int(os.getenv("JWT_ACCESS_TTL_SECONDS", "900"))
JWT_REFRESH_TTL_SECONDS = int(os.getenv("JWT_REFRESH_TTL_SECONDS", "2592000"))

# Provider Settings
OPENROUTER_TIMEOUT = float(os.getenv("OPENROUTER_TIMEOUT", "60.0"))
GROQ_TIMEOUT = float(os.getenv("GROQ_TIMEOUT", "30.0"))
DICTIONARY_TIMEOUT = float(os.getenv("DICTIONARY_TIMEOUT", "5.0"))
DB_TIMEOUT = float(os.getenv("DB_TIMEOUT", "15.0"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Cache Settings
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "604800"))
MAX_CACHE_SIZE = int(os.getenv("MAX_CACHE_SIZE", "1000"))
