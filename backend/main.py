import threading
import time

from contextlib import asynccontextmanager
import logging
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware

# Configure Standard Logger
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "lingofy.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("lingofy.main")

from backend.core.auth import cleanup_expired
from backend.core.config import CORS_ORIGINS, JWT_SECRET
from backend.core.db import init_db
from backend.routes.auth import router as auth_router
from backend.routes.chat import router as chat_router
from backend.routes.lyrics import router as lyrics_router, warmup as lyrics_warmup
from backend.routes.translate import router as translate_router
from backend.routes.spotify import router as spotify_router
from backend.routes.word_info import router as word_info_router
from backend.routes.pronunciation import router as pronunciation_router
from backend.routes.progress import router as progress_router
from backend.routes.subscriptions import router as subscriptions_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not JWT_SECRET:
        raise RuntimeError("JWT_SECRET ortam değişkeni tanımlı değil.")
    init_db()
    threading.Thread(target=lyrics_warmup, daemon=True).start()
    threading.Thread(target=_cleanup_loop, daemon=True).start()
    
    import asyncio
    from backend.core.services.ai_service import get_ai_service
    asyncio.create_task(get_ai_service().health_check())
    
    yield

app = FastAPI(lifespan=lifespan)

# Global Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Geçersiz istek parametreleri.",
                "details": exc.errors()
            }
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail
            }
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled Server Error: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Sunucuda beklenmeyen bir hata oluştu."
            }
        }
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(lyrics_router)
app.include_router(translate_router)
app.include_router(spotify_router)
app.include_router(word_info_router)
app.include_router(pronunciation_router)
app.include_router(progress_router)
app.include_router(subscriptions_router)


def _cleanup_loop():
    while True:
        try:
            removed = cleanup_expired()
            if removed:
                logger.info(f"AUTH CLEANUP: {removed} eski kayıt silindi.")
        except Exception as e:
            logger.error(f"AUTH CLEANUP ERROR: {repr(e)}")
        time.sleep(6 * 60 * 60)  # 6 saatte bir





@app.get("/health")
def health():
    return {"status": "ok"}
