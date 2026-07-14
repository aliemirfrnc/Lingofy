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

from backend.core.logger import get_logger

logger = get_logger("lingofy.main")

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
    
    from backend.admin.migrations.manager import initialize_admin_schema
    initialize_admin_schema()
    
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

import uuid
from backend.core.logger import request_id_ctx, correlation_id_ctx

@app.middleware("http")
async def log_requests_and_set_ids(request: Request, call_next):
    req_id = str(uuid.uuid4())
    corr_id = request.headers.get("X-Correlation-ID", req_id)
    
    token_req = request_id_ctx.set(req_id)
    token_corr = correlation_id_ctx.set(corr_id)
    
    start_time = time.time()
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        
        process_time = time.time() - start_time
        logger.info(f"[{request.method}] {request.url.path} - {response.status_code} - {process_time:.4f}s")
        return response
    except Exception as e:
        logger.exception(f"Unhandled Exception in request {req_id}: {repr(e)}")
        raise
    finally:
        request_id_ctx.reset(token_req)
        correlation_id_ctx.reset(token_corr)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(lyrics_router)
app.include_router(translate_router)
app.include_router(spotify_router)
app.include_router(word_info_router)
app.include_router(pronunciation_router)
app.include_router(progress_router)
app.include_router(subscriptions_router)

from backend.admin.routes.v1 import admin_v1_router
app.include_router(admin_v1_router, prefix="/api/admin/v1", tags=["admin-v1"])

@app.get("/health/liveness", tags=["monitoring"])
async def liveness():
    """Simple check if the application is running."""
    return {"status": "ok", "service": "lingofy-api"}

@app.get("/health/readiness", tags=["monitoring"])
async def readiness():
    """Check if all critical dependencies are ready."""
    from backend.core.db import get_conn
    from backend.core.services.ai_service import get_ai_service
    
    status = {"status": "ok", "components": {}}
    
    # Check DB
    try:
        conn = get_conn()
        conn.cursor().execute("SELECT 1")
        status["components"]["database"] = "ok"
    except Exception as e:
        status["status"] = "degraded"
        status["components"]["database"] = f"error: {str(e)}"
        
    # Check AI circuit breakers
    try:
        ai = get_ai_service()
        groq_status = "ok" if ai.groq.circuit_breaker.can_execute() else "open"
        openrouter_status = "ok" if ai.openrouter.circuit_breaker.can_execute() else "open"
        status["components"]["ai_groq"] = groq_status
        status["components"]["ai_openrouter"] = openrouter_status
    except Exception as e:
        status["status"] = "degraded"
        status["components"]["ai"] = f"error: {str(e)}"
        
    return JSONResponse(
        status_code=200 if status["status"] == "ok" else 503,
        content=status
    )


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
