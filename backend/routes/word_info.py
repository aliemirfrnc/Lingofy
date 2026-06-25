import os
import json
import threading
import asyncio
import httpx
import time

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel, Field

from backend.core.cache_store import load, save
from backend.routes.auth import require_user_id
from backend.dependencies.subscription import enforce_usage_limit
from backend.core.services.ai_service import get_ai_service
from backend.core.services.dictionary_service import DictionaryService, TranslationService
from backend.core.db import get_conn, get_lock
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["words"])

_cache: dict[str, dict] = load("word_info")
_cache_lock = threading.Lock()

class WordInfoRequest(BaseModel):
    word: str
    context_line: str = ""

class WordProgressRequest(BaseModel):
    word: str

class WordInfoResponse(BaseModel):
    word: str
    turkish_meanings: list[str]
    part_of_speech: str
    pronunciation: str
    definition: str
    grammar_note: str
    synonyms: list[str]
    antonyms: list[str]
    examples: list[str]
    collocations: list[str]
    phrasal_verbs: list[str]
    word_family: list[str]
    syllables: str
    contextual_meaning: str
    ai_learning_tip: str
    times_seen: int
    learning_percentage: int
    last_seen: float
    first_seen: float
    is_favorite: bool
    is_memorized: bool
    mastery_level: str
    review_count: int

class WordInfoContextSchema(BaseModel):
    contextual_meaning: str = Field(description="Şarkı sözü bağlamındaki çevirisi ve anlamı")
    ai_learning_tip: str = Field(description="Öğrenmeyi kolaylaştıracak pratik ipucu")

def _clean_word(raw: str) -> str:
    return raw.strip(".,!?;:\"'()[]{}…—-").lower()

def _update_user_word_progress(user_id: int, word: str):
    conn = get_conn()
    now = time.time()
    try:
        with get_lock():
            cursor = conn.cursor()
            cursor.execute("SELECT times_seen, is_memorized FROM user_words WHERE user_id = ? AND word = ?", (user_id, word))
            row = cursor.fetchone()
            
            if row:
                times_seen = row[0] + 1
                is_memorized = row[1]
                
                # Simple learning percentage logic
                perc = min(100, times_seen * 10)
                if is_memorized: perc = 100
                
                mastery = "New"
                if perc > 30: mastery = "Learning"
                if perc > 70: mastery = "Familiar"
                if perc == 100: mastery = "Mastered"
                
                cursor.execute("""
                    UPDATE user_words 
                    SET times_seen = ?, last_seen = ?, learning_percentage = ?, mastery_level = ?, updated_at = ?
                    WHERE user_id = ? AND word = ?
                """, (times_seen, now, perc, mastery, now, user_id, word))
            else:
                cursor.execute("""
                    INSERT INTO user_words (user_id, word, times_seen, learning_percentage, last_seen, first_seen, created_at, updated_at)
                    VALUES (?, ?, 1, 10, ?, ?, ?, ?)
                """, (user_id, word, now, now, now, now))
            conn.commit()
    except Exception as e:
        logger.error(f"DB Error tracking word progress: {e}")

def _get_user_word_progress(user_id: int, word: str) -> dict:
    conn = get_conn()
    try:
        with get_lock():
            cursor = conn.cursor()
            cursor.execute("SELECT times_seen, learning_percentage, last_seen, first_seen, is_favorite, is_memorized, mastery_level, review_count FROM user_words WHERE user_id = ? AND word = ?", (user_id, word))
            row = cursor.fetchone()
            if row:
                return {
                    "times_seen": row[0],
                    "learning_percentage": row[1],
                    "last_seen": row[2],
                    "first_seen": row[3],
                    "is_favorite": bool(row[4]),
                    "is_memorized": bool(row[5]),
                    "mastery_level": row[6],
                    "review_count": row[7]
                }
    except Exception as e:
        logger.error(f"DB Error getting word progress: {e}")
        
    return {
        "times_seen": 1,
        "learning_percentage": 10,
        "last_seen": time.time(),
        "first_seen": time.time(),
        "is_favorite": False,
        "is_memorized": False,
        "mastery_level": "New",
        "review_count": 0
    }

@router.post("/word-info", response_model=WordInfoResponse)
@enforce_usage_limit(feature="words")
async def word_info(
    payload: WordInfoRequest,
    request: Request,
    authorization: str | None = Header(default=None)
):
    user_id = require_user_id(request, authorization)
    
    word = _clean_word(payload.word)
    if not word:
        raise HTTPException(status_code=400, detail="Geçersiz kelime.")

    _update_user_word_progress(user_id, word)
    progress = _get_user_word_progress(user_id, word)

    cache_key = f"{word}::{payload.context_line.strip().lower()}"

    with _cache_lock:
        if cache_key in _cache:
            cached_data = _cache[cache_key].copy()
            cached_data.update(progress)
            return cached_data

    async def _get_ai_context():
        if not payload.context_line:
            return {"contextual_meaning": "", "ai_learning_tip": ""}
        try:
            ai_service = get_ai_service()
            sys_prompt = "Sen bir sözlük asistanısın. Sadece verilen kelimenin şarkı sözü bağlamındaki anlamını ve kısa bir pratik öğrenme ipucunu döndür."
            usr_prompt = f"Kelime: {word}\nBağlam: {payload.context_line}"
            ai_data = await ai_service.get_word_context(
                system_prompt=sys_prompt,
                user_prompt=usr_prompt,
                schema=WordInfoContextSchema
            )
            return {
                "contextual_meaning": ai_data.get("contextual_meaning", ""),
                "ai_learning_tip": ai_data.get("ai_learning_tip", "")
            }
        except Exception as e:
            logger.error(f"WORD INFO AI ERROR: {repr(e)}")
            return {"contextual_meaning": "", "ai_learning_tip": ""}

    # 1, 2 & 3. Run Dictionary, Translation, and AI tasks concurrently
    dict_data, translation, ai_data = await asyncio.gather(
        DictionaryService.get_word_definition(word),
        TranslationService.get_turkish_translation(word),
        _get_ai_context()
    )

    result = {
        "word": word,
        "turkish_meanings": [translation] if translation and translation != word else [],
        "part_of_speech": dict_data.get("part_of_speech", ""),
        "pronunciation": dict_data.get("pronunciation", ""),
        "definition": dict_data.get("definition", ""),
        "grammar_note": "",
        "synonyms": dict_data.get("synonyms", []),
        "antonyms": dict_data.get("antonyms", []),
        "examples": dict_data.get("examples", []),
        "collocations": [],
        "phrasal_verbs": [],
        "word_family": [],
        "syllables": "",
        "contextual_meaning": ai_data["contextual_meaning"],
        "ai_learning_tip": ai_data["ai_learning_tip"]
    }

    with _cache_lock:
        _cache[cache_key] = result
        save("word_info", _cache)

    result_with_progress = result.copy()
    result_with_progress.update(progress)
    return result_with_progress

@router.post("/words/favorite")
async def toggle_favorite(
    payload: WordProgressRequest,
    request: Request,
    authorization: str | None = Header(default=None)
):
    user_id = require_user_id(request, authorization)
    word = _clean_word(payload.word)
    conn = get_conn()
    try:
        with get_lock():
            cursor = conn.cursor()
            cursor.execute("SELECT is_favorite FROM user_words WHERE user_id = ? AND word = ?", (user_id, word))
            row = cursor.fetchone()
            new_val = False
            if row:
                new_val = not bool(row[0])
                cursor.execute("UPDATE user_words SET is_favorite = ?, updated_at = ? WHERE user_id = ? AND word = ?", (new_val, time.time(), user_id, word))
            else:
                new_val = True
                cursor.execute("INSERT INTO user_words (user_id, word, is_favorite, last_seen, first_seen, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                              (user_id, word, True, time.time(), time.time(), time.time(), time.time()))
            conn.commit()
            return {"success": True, "is_favorite": new_val}
    except Exception as e:
        logger.error(f"Toggle Favorite DB Error: {e}")
        raise HTTPException(status_code=503, detail="İşlem şu anda gerçekleştirilemiyor. Lütfen tekrar dene.")

@router.post("/words/memorize")
async def toggle_memorize(
    payload: WordProgressRequest,
    request: Request,
    authorization: str | None = Header(default=None)
):
    user_id = require_user_id(request, authorization)
    word = _clean_word(payload.word)
    conn = get_conn()
    try:
        with get_lock():
            cursor = conn.cursor()
            cursor.execute("SELECT is_memorized, times_seen FROM user_words WHERE user_id = ? AND word = ?", (user_id, word))
            row = cursor.fetchone()
            new_val = False
            if row:
                new_val = not bool(row[0])
                perc = 100 if new_val else min(100, row[1] * 10)
                mastery = "Mastered" if new_val else ("Familiar" if perc > 70 else "Learning")
                cursor.execute("UPDATE user_words SET is_memorized = ?, learning_percentage = ?, mastery_level = ?, updated_at = ? WHERE user_id = ? AND word = ?", 
                               (new_val, perc, mastery, time.time(), user_id, word))
            else:
                new_val = True
                cursor.execute("INSERT INTO user_words (user_id, word, is_memorized, learning_percentage, mastery_level, last_seen, first_seen, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                              (user_id, word, True, 100, "Mastered", time.time(), time.time(), time.time(), time.time()))
            conn.commit()
            return {"success": True, "is_memorized": new_val}
    except Exception as e:
        logger.error(f"Toggle Memorize DB Error: {e}")
        raise HTTPException(status_code=503, detail="İşlem şu anda gerçekleştirilemiyor. Lütfen tekrar dene.")

@router.post("/words/review")
async def toggle_review(
    payload: WordProgressRequest,
    request: Request,
    authorization: str | None = Header(default=None)
):
    user_id = require_user_id(request, authorization)
    word = _clean_word(payload.word)
    conn = get_conn()
    try:
        with get_lock():
            cursor = conn.cursor()
            cursor.execute("SELECT review_count FROM user_words WHERE user_id = ? AND word = ?", (user_id, word))
            row = cursor.fetchone()
            if row:
                new_count = row[0] + 1
                cursor.execute("UPDATE user_words SET review_count = ?, updated_at = ? WHERE user_id = ? AND word = ?", 
                               (new_count, time.time(), user_id, word))
            else:
                new_count = 1
                cursor.execute("INSERT INTO user_words (user_id, word, review_count, last_seen, first_seen, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                              (user_id, word, 1, time.time(), time.time(), time.time(), time.time()))
            conn.commit()
            return {"success": True, "review_count": new_count}
    except Exception as e:
        logger.error(f"Toggle Review DB Error: {e}")
        raise HTTPException(status_code=503, detail="İşlem şu anda gerçekleştirilemiyor. Lütfen tekrar dene.")

