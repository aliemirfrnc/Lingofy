import asyncio
import httpx
import logging
from typing import Dict, Any
from backend.core.logger import get_logger
from backend.core.config import DICTIONARY_TIMEOUT

logger = get_logger(__name__)

class DictionaryService:
    @classmethod
    async def get_word_definition(cls, word: str) -> Dict[str, Any]:
        dict_data = {
            "pronunciation": "",
            "part_of_speech": "",
            "definition": "",
            "examples": [],
            "synonyms": [],
            "antonyms": []
        }
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
                    if resp.status_code == 200:
                        entries = resp.json()
                        if entries and isinstance(entries, list):
                            entry = entries[0]
                            dict_data["pronunciation"] = entry.get("phonetic", "")
                            if not dict_data["pronunciation"] and entry.get("phonetics"):
                                for ph in entry["phonetics"]:
                                    if ph.get("text"):
                                        dict_data["pronunciation"] = ph["text"]
                                        break
                            meanings = entry.get("meanings", [])
                            if meanings:
                                m = meanings[0]
                                dict_data["part_of_speech"] = m.get("partOfSpeech", "")
                                defs = m.get("definitions", [])
                                if defs:
                                    dict_data["definition"] = defs[0].get("definition", "")
                                    dict_data["examples"] = [defs[0].get("example")] if defs[0].get("example") else []
                                dict_data["synonyms"] = m.get("synonyms", [])
                                dict_data["antonyms"] = m.get("antonyms", [])
                        return dict_data
                    elif resp.status_code == 404:
                        return dict_data # Word not found, no need to retry
                    elif resp.status_code == 429:
                        retry_after = resp.headers.get("Retry-After")
                        sleep_time = float(retry_after) if retry_after else 1.0
                        await asyncio.sleep(sleep_time)
                        continue
                        
                    resp.raise_for_status()
            except Exception as e:
                logger.warning(f"DICTIONARY API ERROR on attempt {attempt+1}: {repr(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    
        return dict_data

class TranslationService:
    @staticmethod
    async def get_turkish_translation(word: str) -> str:
        from deep_translator import GoogleTranslator
        max_retries = 2
        for attempt in range(max_retries):
            try:
                translator = GoogleTranslator(source='en', target='tr')
                translation = await asyncio.to_thread(translator.translate, word)
                return translation
            except Exception as e:
                logger.warning(f"TRANSLATION ERROR on attempt {attempt+1}: {repr(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
        return word
