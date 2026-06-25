import asyncio
import time
import logging
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.core.cache_store import get_cache, save
from backend.routes.auth import require_user_id

router = APIRouter()

# 24 hours TTL cache
_cache = get_cache("translations", ttl_seconds=86400)
_cache_lock = asyncio.Lock()

_rate_limit: dict[int, tuple[date, int]] = {}
_rate_limit_lock = asyncio.Lock()
DAILY_LIMIT = 500

# Concurrency limit for translations
_translate_semaphore = asyncio.Semaphore(3)

class TranslateRequest(BaseModel):
    text: str
    track_id: Optional[str] = None

class TranslateResponse(BaseModel):
    translation: str

class TranslateBatchRequest(BaseModel):
    lines: list[str]
    track_id: Optional[str] = None

class TranslateBatchResponse(BaseModel):
    translations: dict[str, str]
    failed: list[str]

async def _check_rate_limit(user_id: int, cost: int = 1) -> None:
    async with _rate_limit_lock:
        today = date.today()
        last_date, count = _rate_limit.get(user_id, (today, 0))

        if last_date != today:
            count = 0

        if count + cost > DAILY_LIMIT:
            raise HTTPException(status_code=429, detail="Günlük çeviri limitine ulaştın.")

        _rate_limit[user_id] = (today, count + cost)

async def _translate_cached(text: str, track_id: str | None = None) -> tuple[str | None, bool]:
    text_strip = text.strip()
    if not text_strip:
        return "", False

    key = f"{track_id}_{text_strip}" if track_id else text_strip

    # 1. Cache Check
    async with _cache_lock:
        if key in _cache:
            logging.info(f"[Translation] Provider: Cache | Latency: 0ms | Hit: {key[:30]}")
            return _cache[key], False

    start_time = time.time()
    result = None
    fallback_used = False
    provider = "Groq"

    async with _translate_semaphore:
        try:
            from backend.core.providers.groq_provider import GroqProvider
            groq = GroqProvider()
            prompt = "Sadece doğal Türkçe çeviri üret. Şiirsel yapıyı koru. Açıklama yazma. JSON üretme. Tek satır döndür."
            result = await groq.generate(system_prompt=prompt, user_prompt=text_strip, temperature=0.1)
            # AI bazen tırnak işareti içinde döndürebiliyor, onları temizleyelim
            if result.startswith('"') and result.endswith('"'):
                result = result[1:-1]
            result = result.strip()
        except Exception as e:
            logging.warning(f"Groq translation failed: {repr(e)}. Falling back to DeepTranslator.")
            fallback_used = True
            provider = "DeepTranslator"
            try:
                from backend.core.services.dictionary_service import TranslationService
                result = await TranslationService.get_turkish_translation(text_strip)
            except Exception as fallback_e:
                logging.error(f"Fallback translation also failed: {repr(fallback_e)}")
                result = None

    latency = int((time.time() - start_time) * 1000)
    
    if result:
        logging.info(f"[Translation] Provider: {provider} | Latency: {latency}ms | Cache: MISS | Fallback: {fallback_used}")
        async with _cache_lock:
            _cache[key] = result
        return result, True
    
    logging.info(f"[Translation] Provider: None | Latency: {latency}ms | Cache: MISS | Fallback: Failed")
    return None, False

@router.post("/translate-line", response_model=TranslateResponse)
async def translate_line(request: TranslateRequest, user_id: int = Depends(require_user_id)):
    await _check_rate_limit(user_id)

    result, added = await _translate_cached(request.text, request.track_id)
    if result is None:
        return {"translation": request.text} # Orijinal metin dönsün (Fallback from error)

    if added:
        async with _cache_lock:
            save("translations") # save call does not need `_cache` dict anymore since get_cache handles it

    return {"translation": result}

@router.post("/translate-batch", response_model=TranslateBatchResponse)
async def translate_batch(request: TranslateBatchRequest, user_id: int = Depends(require_user_id)):
    lines = [l for l in request.lines if l.strip()]
    await _check_rate_limit(user_id, cost=max(1, len(lines)))

    results: dict[str, str] = {}
    failed: list[str] = []
    any_added = False

    tasks = [_translate_cached(line, request.track_id) for line in lines]
    outcomes = await asyncio.gather(*tasks, return_exceptions=True)

    for line, outcome in zip(lines, outcomes):
        if isinstance(outcome, Exception) or outcome[0] is None:
            failed.append(line)
        else:
            results[line] = outcome[0]
            any_added = any_added or outcome[1]

    if any_added:
        async with _cache_lock:
            save("translations")

    return {"translations": results, "failed": failed}
