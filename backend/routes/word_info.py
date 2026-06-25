import os
import json
import threading

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel, Field

from backend.core.cache_store import load, save
from backend.routes.auth import require_user_id
from backend.dependencies.subscription import enforce_usage_limit
from backend.core.providers.ai_factory import get_ai_provider

router = APIRouter()

_cache: dict[str, dict] = load("word_info")
_cache_lock = threading.Lock()

with open(os.path.join(os.path.dirname(__file__), "..", "prompts", "word_system.txt"), "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read().strip()

class WordInfoRequest(BaseModel):
    word: str
    context_line: str = ""

class WordInfoResponse(BaseModel):
    word: str
    translation: str
    part_of_speech: str
    pronunciation: str
    definition: str
    contextual_meaning: str
    register_: str = Field(alias="register", serialization_alias="register")
    frequency: str
    grammar_note: str
    synonyms: list[str]
    antonyms: list[str]
    examples: list[str]
    usage_note: str

class WordInfoSchema(BaseModel):
    translation: str
    part_of_speech: str
    pronunciation: str
    definition: str
    contextual_meaning: str
    register: str
    frequency: str
    grammar_note: str
    synonyms: list[str]
    antonyms: list[str]
    examples: list[str]
    usage_note: str

def _clean_word(raw: str) -> str:
    return raw.strip(".,!?;:\"'()[]{}…—-").lower()

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

    cache_key = f"{word}::{payload.context_line.strip().lower()}"

    with _cache_lock:
        if cache_key in _cache:
            return _cache[cache_key]

    user_prompt = f'Word: "{word}"'
    if payload.context_line:
        user_prompt += f'\nLine it appears in (context only, do not reuse verbatim): "{payload.context_line}"'

    try:
        provider = get_ai_provider()
        data = await provider.generate_json(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema=WordInfoSchema,
            temperature=0.4
        )
    except Exception as e:
        print("WORD INFO ERROR:", repr(e))
        raise HTTPException(status_code=500, detail="Kelime bilgisi alınamadı.")

    result = {
        "word": word,
        "translation": data.get("translation", ""),
        "part_of_speech": data.get("part_of_speech", ""),
        "pronunciation": data.get("pronunciation", ""),
        "definition": data.get("definition", ""),
        "contextual_meaning": data.get("contextual_meaning", ""),
        "register": data.get("register", ""),
        "frequency": data.get("frequency", ""),
        "grammar_note": data.get("grammar_note", ""),
        "synonyms": data.get("synonyms") or [],
        "antonyms": data.get("antonyms") or [],
        "examples": data.get("examples") or [],
        "usage_note": data.get("usage_note", ""),
    }

    with _cache_lock:
        _cache[cache_key] = result
        save("word_info", _cache)

    return result
