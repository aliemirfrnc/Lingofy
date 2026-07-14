import json
import time
import asyncio
import httpx
import logging
from typing import Any, Dict, List, Optional, Type, AsyncGenerator
from pydantic import BaseModel
import json_repair

from backend.core.config import GROQ_API_KEY, GROQ_MODEL
from backend.core.providers.ai_provider import AIProvider
from backend.core.providers.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

class GroqProvider(AIProvider):
    _instance = None

    def __new__(cls):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY bulunamadı!")
            
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = httpx.AsyncClient(
                base_url="https://api.groq.com/openai/v1",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY.strip()}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            cls._instance.circuit_breaker = CircuitBreaker()
            cls._instance.metrics = {
                "total_requests": 0,
                "successes": 0,
                "failures": 0,
                "retries": 0,
                "total_latency": 0.0,
                "tokens_in": 0,
                "tokens_out": 0
            }
        return cls._instance

    @property
    def client(self):
        return self._client

    async def _execute_with_retry(self, method_name: str, payload: dict) -> httpx.Response:
        self.metrics["total_requests"] += 1
        if not self.circuit_breaker.can_execute():
            self.metrics["failures"] += 1
            raise Exception("Circuit Breaker OPEN: Groq is currently unavailable.")

        max_retries = 3
        backoff_times = [1, 2, 4]
        
        for attempt in range(max_retries):
            start_time = time.time()
            try:
                response = await self.client.post("/chat/completions", json=payload)
                
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    sleep_time = float(retry_after) if retry_after else backoff_times[attempt]
                    logger.warning(f"[Groq] Rate limited. Retrying in {sleep_time}s...")
                    self.metrics["retries"] += 1
                    await asyncio.sleep(sleep_time)
                    continue
                    
                response.raise_for_status()
                
                latency = time.time() - start_time
                self.metrics["total_latency"] += latency
                
                data = response.json()
                usage = data.get("usage", {})
                tokens_in = usage.get("prompt_tokens", 0)
                tokens_out = usage.get("completion_tokens", 0)
                
                self.metrics["tokens_in"] += tokens_in
                self.metrics["tokens_out"] += tokens_out
                self.metrics["successes"] += 1
                self.circuit_breaker.record_success()
                
                logger.info(f"[Groq] {method_name} | Model: {payload.get('model')} | Latency: {latency:.2f}s | Tokens: {tokens_in} in, {tokens_out} out | Attempt: {attempt+1}")
                return response
                
            except httpx.HTTPStatusError as e:
                logger.error(f"[Groq] HTTP Error {e.response.status_code} for {method_name}: {e.response.text}")
                if e.response.status_code not in [429, 500, 502, 503, 504]:
                    self.metrics["failures"] += 1
                    self.circuit_breaker.record_failure()
                    raise
                
                self.metrics["retries"] += 1
                if attempt < max_retries - 1:
                    await asyncio.sleep(backoff_times[attempt])
                else:
                    self.metrics["failures"] += 1
                    self.circuit_breaker.record_failure()
                    raise
            except Exception as e:
                logger.warning(f"[Groq] Attempt {attempt + 1} failed for {method_name}: {repr(e)}")
                self.metrics["retries"] += 1
                if attempt < max_retries - 1:
                    await asyncio.sleep(backoff_times[attempt])
                else:
                    self.metrics["failures"] += 1
                    self.circuit_breaker.record_failure()
                    raise
        
        self.metrics["failures"] += 1
        self.circuit_breaker.record_failure()
        raise Exception(f"All retries exhausted for [Groq] {method_name}.")

    async def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        response = await self._execute_with_retry("generate", payload)
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def generate_json(self, system_prompt: str, user_prompt: str, schema: Type[BaseModel] | None = None, temperature: float = 0.0) -> Dict[str, Any]:
        if schema:
            schema_json = json.dumps(schema.model_json_schema(), ensure_ascii=False)
            system_prompt += f"\n\nLütfen aşağıdaki JSON şemasına KESİNLİKLE uyan bir çıktı üret:\n{schema_json}"

        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt + "\n\nLütfen sadece geçerli bir JSON objesi dön, Markdown kullanma, Kod bloğu kullanma."},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"}
        }

        max_attempts = 2
        for attempt in range(max_attempts):
            response = await self._execute_with_retry("generate_json", payload)
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            
            try:
                parsed = json_repair.repair_json(content, return_objects=True)
                if isinstance(parsed, list) and len(parsed) > 0:
                    parsed = parsed[0]
                if not isinstance(parsed, dict):
                    raise ValueError(f"JSON objesi (dict) bekleniyordu.")

                if schema:
                    schema(**parsed) 
                
                return parsed
            except Exception as e:
                if attempt == max_attempts - 1:
                    logger.error(f"[Groq] JSON Validation Error: {e} | Content: {content}")
                    raise ValueError(f"Geçersiz JSON formatı: {content}")
                
                logger.warning(f"[Groq] JSON Validation Error, retrying... Attempt {attempt+1}")
                payload["messages"][-1]["content"] += "\n\nÖnceki cevabın geçerli JSON değildi. Sadece geçerli JSON döndür. Markdown kullanma. Kod bloğu kullanma. Hiçbir açıklama ekleme."

    async def chat(self, system_prompt: str, messages: List[Dict[str, str]], temperature: float = 0.6) -> str:
        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "temperature": temperature
        }
        response = await self._execute_with_retry("chat", payload)
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def stream(self, system_prompt: str, messages: List[Dict[str, str]], temperature: float = 0.6) -> AsyncGenerator[str, None]:
        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "temperature": temperature,
            "stream": True
        }
        
        try:
            async with self.client.stream("POST", "/chat/completions", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            chunk = data["choices"][0]["delta"].get("content", "")
                            if chunk:
                                yield chunk
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"[Groq] Streaming failed: {repr(e)}")
            yield f"\n[Bağlantı Hatası: {str(e)}]"

    async def summarize(self, text: str) -> str:
        return await self.generate(system_prompt="Aşağıdaki metni kısaca özetle.", user_prompt=text, temperature=0.3)
        
    async def translate(self, text: str) -> str:
        import os
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "translation", "system.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                sys_prompt = f.read().strip()
        else:
            sys_prompt = "Aşağıdaki cümleyi İngilizceden Türkçeye kelimesi kelimesine değil, anlam odaklı çevir."
        return await self.generate(system_prompt=sys_prompt, user_prompt=text, temperature=0.0)
        
    async def pronunciation_feedback(self, tech_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Pronunciation feedback should use OpenRouter.")
