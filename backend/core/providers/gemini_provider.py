import os
import time
import json
import logging
import asyncio
from typing import Any, Dict, Type
from pydantic import BaseModel

from google import genai
from google.genai import types

from backend.core.config import GEMINI_API_KEY, GEMINI_MODEL
from backend.core.providers.ai_provider import AIProvider

logger = logging.getLogger("ai_provider")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

class GeminiProvider(AIProvider):
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_client()
        return cls._instance
        
    def _init_client(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        
    def _log_request(self, method: str, model: str, latency: float, retries: int, tokens_in: int, tokens_out: int, status: str):
        total_tokens = tokens_in + tokens_out
        logger.info(
            f"Provider: Gemini | Model: {model} | Method: {method} | "
            f"Status: {status} | Latency: {latency:.2f}s | Retries: {retries} | "
            f"Tokens: {tokens_in} in + {tokens_out} out = {total_tokens} total"
        )
        
    async def generate_json(self, system_prompt: str, user_prompt: str, schema: Type[BaseModel] | None = None, temperature: float = 0.4) -> Dict[str, Any]:
        return await self._execute_with_retry("generate_json", system_prompt, user_prompt, temperature, response_schema=schema)

    async def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        return await self._execute_with_retry("generate_text", system_prompt, user_prompt, temperature, response_schema=None)

    async def transcribe_audio(self, audio_path: str) -> str:
        max_retries = 3
        backoff_times = [1, 2, 4]
        
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
            
        # Determine mime type based on extension
        mime_type = "audio/webm"
        if audio_path.endswith(".mp3"):
            mime_type = "audio/mp3"
        elif audio_path.endswith(".wav"):
            mime_type = "audio/wav"
            
        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
        prompt = "Accurately transcribe this English audio. Do not add any extra commentary, just the transcription."
        
        config = types.GenerateContentConfig(temperature=0.0)
        
        for attempt in range(max_retries):
            start_time = time.time()
            try:
                response = await self.client.aio.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=[audio_part, prompt],
                    config=config
                )
                
                latency = time.time() - start_time
                usage = response.usage_metadata
                tokens_in = usage.prompt_token_count if usage else 0
                tokens_out = usage.candidates_token_count if usage else 0
                
                self._log_request("transcribe_audio", GEMINI_MODEL, latency, attempt, tokens_in, tokens_out, "200 OK")
                return response.text.strip()
                
            except Exception as e:
                latency = time.time() - start_time
                logger.warning(f"Attempt {attempt + 1} failed for transcribe_audio: {repr(e)}")
                if attempt < len(backoff_times):
                    await asyncio.sleep(backoff_times[attempt])
                else:
                    self._log_request("transcribe_audio", GEMINI_MODEL, latency, attempt, 0, 0, "500 ERROR")
                    logger.error(f"All retries exhausted for transcribe_audio.")
                    raise

    async def _execute_with_retry(self, method_name: str, system_prompt: str, user_prompt: str, temperature: float, response_schema: Type[BaseModel] | None) -> Any:
        max_retries = 3
        backoff_times = [1, 2, 4]
        
        config_kwargs = {
            "system_instruction": system_prompt,
            "temperature": temperature,
        }
        
        if response_schema:
            config_kwargs["response_mime_type"] = "application/json"
            config_kwargs["response_schema"] = response_schema
            
        config = types.GenerateContentConfig(**config_kwargs)
        
        for attempt in range(max_retries):
            start_time = time.time()
            try:
                response = await self.client.aio.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=user_prompt,
                    config=config
                )
                
                latency = time.time() - start_time
                usage = response.usage_metadata
                tokens_in = usage.prompt_token_count if usage else 0
                tokens_out = usage.candidates_token_count if usage else 0
                
                self._log_request(method_name, GEMINI_MODEL, latency, attempt, tokens_in, tokens_out, "200 OK")
                
                if response_schema:
                    try:
                        return json.loads(response.text)
                    except json.JSONDecodeError:
                        text = response.text.strip()
                        start_idx = text.find('{')
                        end_idx = text.rfind('}')
                        if start_idx != -1 and end_idx != -1:
                            return json.loads(text[start_idx:end_idx+1])
                        raise
                return response.text
                
            except Exception as e:
                latency = time.time() - start_time
                logger.warning(f"Attempt {attempt + 1} failed for {method_name}: {repr(e)}")
                if attempt < len(backoff_times):
                    await asyncio.sleep(backoff_times[attempt])
                else:
                    self._log_request(method_name, GEMINI_MODEL, latency, attempt, 0, 0, "500 ERROR")
                    logger.error(f"All retries exhausted for {method_name}.")
                    raise
