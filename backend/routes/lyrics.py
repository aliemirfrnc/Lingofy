import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel

from backend.core.cache_store import load, save

router = APIRouter()


class SyncedLine(BaseModel):
    time: float
    text: str


class LyricsResponse(BaseModel):
    lyrics: list[str]
    synced: list[SyncedLine] | None = None
    source: str


_cache: dict[str, dict] = load("lyrics")
_cache_lock = threading.Lock()
_thread_local = threading.local()

_executor = ThreadPoolExecutor(max_workers=4)

HEADERS = {"User-Agent": "Lingofy/1.0"}
TIMEOUT = 15
WARMUP_WORKERS = 2

from backend.core.services.lrclib_service import LrclibService

def warmup() -> None:
    """Backend açılışında LRCLIB'e bağlantıyı önceden ısıtır."""
    LrclibService.warmup(WARMUP_WORKERS)


@router.get("/lyrics", response_model=LyricsResponse)
def get_lyrics(
    background_tasks: BackgroundTasks,
    track: str = Query(...),
    artist: str = Query(""),
):
    cache_key = f"{track.lower()}::{artist.lower()}"

    with _cache_lock:
        cached = _cache.get(cache_key)
    if cached:
        return {**cached, "source": "LRCLIB (cache)"}

    data, had_network_error = LrclibService.fetch_lyrics(track, artist)

    if not data:
        if had_network_error:
            raise HTTPException(
                status_code=502,
                detail="Şarkı sözü servisi şu anda yanıt vermiyor. Lütfen tekrar deneyin.",
            )
        raise HTTPException(status_code=404, detail="Bu şarkı için söz bulunamadı.")

    with _cache_lock:
        _cache[cache_key] = data

    background_tasks.add_task(save, "lyrics", _cache)

    return {**data, "source": "LRCLIB"}
