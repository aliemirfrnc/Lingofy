import json
import time
import asyncio
import httpx
import logging
from typing import Any, Dict, List, Optional, Type, AsyncGenerator
from pydantic import BaseModel

from backend.core.config import (
    OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_BASE_URL,
    OPENROUTER_SITE_URL, OPENROUTER_APP_NAME
)
from backend.core.providers.ai_provider import AIProvider

logger = logging.getLogger(__name__)

class OpenRouterProvider(AIProvider):
    _instance = None

    def __new__(cls):
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY bulunamadı! Lütfen .env dosyanızı kontrol edin.")
            
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = httpx.AsyncClient(
                base_url=OPENROUTER_BASE_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY.strip()}",
                    "HTTP-Referer": OPENROUTER_SITE_URL,
                    "X-Title": OPENROUTER_APP_NAME,
                    "Content-Type": "application/json"
                },
                timeout=60.0
            )
            from backend.core.providers.circuit_breaker import CircuitBreaker
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
            raise Exception("Circuit Breaker OPEN: OpenRouter is currently unavailable.")

        max_retries = 3
        backoff_times = [1, 2, 4, 8]
        
        for attempt in range(max_retries):
            start_time = time.time()
            try:
                response = await self.client.post("/chat/completions", json=payload)
                
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    sleep_time = float(retry_after) if retry_after else backoff_times[attempt]
                    logger.warning(f"Rate limited. Retrying in {sleep_time}s...")
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
                
                logger.info(f"[OpenRouter] {method_name} | Model: {data.get('model', 'unknown')} | Latency: {latency:.2f}s | Tokens: {tokens_in} in, {tokens_out} out | Attempt: {attempt+1}")
                return response
                
            except httpx.HTTPStatusError as e:
                logger.error(f"[OpenRouter] HTTP Error {e.response.status_code} for {method_name}: {e.response.text}")
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
                logger.warning(f"[OpenRouter] Attempt {attempt + 1} failed for {method_name}: {repr(e)}")
                self.metrics["retries"] += 1
                if attempt < max_retries - 1:
                    await asyncio.sleep(backoff_times[attempt])
                else:
                    self.metrics["failures"] += 1
                    self.circuit_breaker.record_failure()
                    raise
        
        self.metrics["failures"] += 1
        self.circuit_breaker.record_failure()
        raise Exception(f"All retries exhausted for [OpenRouter] {method_name}.")

    async def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        
        # OpenRouter cross-provider fallback
        payload["models"] = [
            OPENROUTER_MODEL,
            "deepseek/deepseek-chat",
            "openai/gpt-4o-mini"
        ]

        response = await self._execute_with_retry("generate", payload)
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def generate_json(self, system_prompt: str, user_prompt: str, schema: Type[BaseModel] | None = None, temperature: float = 0.4) -> Dict[str, Any]:
        import json_repair

        if schema:
            schema_json = json.dumps(schema.model_json_schema(), ensure_ascii=False)
            system_prompt += f"\n\nLütfen aşağıdaki JSON şemasına (schema) KESİNLİKLE uyan bir çıktı üret:\n{schema_json}"

        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt + "\n\nLütfen sadece geçerli bir JSON objesi dön, ekstra hiçbir açıklama yapma."},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }

        payload["models"] = [
            OPENROUTER_MODEL,
            "deepseek/deepseek-chat",
            "openai/gpt-4o-mini"
        ]

        max_attempts = 2
        for attempt in range(max_attempts):
            response = await self._execute_with_retry("generate_json", payload)
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()
            
            try:
                # 1. JSON Repair
                parsed = json_repair.repair_json(content, return_objects=True)
                
                # 2. Eğer liste dönerse ve biz dict bekliyorsak
                if isinstance(parsed, list) and len(parsed) > 0:
                    parsed = parsed[0]
                    
                if not isinstance(parsed, dict):
                    raise ValueError(f"JSON objesi (dict) bekleniyordu ancak {type(parsed)} geldi.")

                # 3. Pydantic ile Doğrula
                if schema:
                    schema(**parsed) 
                
                return parsed
            except Exception as e:
                # Herhangi bir parse veya pydantic hatasında süreci yakala
                if attempt == max_attempts - 1:
                    logger.error(f"JSON Validation/Repair Error: {e} | Content: {content}")
                    raise ValueError(f"Geçersiz JSON formatı: {content}")
                
                logger.warning(f"JSON Validation/Repair Error, retrying... Attempt {attempt+1}")
                # İkinci istek için katı uyarı ekle
                payload["messages"][-1]["content"] += "\n\nÖnceki cevabın geçerli JSON değildi veya şemaya uymuyordu. Lütfen yalnızca geçerli JSON döndür! Markdown kullanma. Kod bloğu kullanma. Şema dışına çıkma."

    async def chat(self, system_prompt: str, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "temperature": temperature
        }
        
        payload["models"] = [
            OPENROUTER_MODEL,
            "deepseek/deepseek-chat",
            "openai/gpt-4o-mini"
        ]

        response = await self._execute_with_retry("chat", payload)
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def stream(self, system_prompt: str, messages: List[Dict[str, str]], temperature: float = 0.7) -> AsyncGenerator[str, None]:
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "temperature": temperature,
            "stream": True
        }
        
        payload["models"] = [
            OPENROUTER_MODEL,
            "deepseek/deepseek-chat",
            "openai/gpt-4o-mini"
        ]

        start_time = time.time()
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
            logger.error(f"Streaming failed: {repr(e)}")
            yield f"\n[Bağlantı Hatası: {str(e)}]"
            
    async def summarize(self, text: str) -> str:
        # Implement summarization directly via generate
        import os
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "summarize.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                system = f.read()
        else:
            system = "Aşağıdaki metni kısaca özetle."
        return await self.generate(system_prompt=system, user_prompt=text, temperature=0.3)
        
    async def translate(self, text: str) -> str:
        import os
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "translation.txt")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as f:
                system = f.read()
        else:
            system = "Aşağıdaki cümleyi İngilizceden Türkçeye kelimesi kelimesine değil, anlam odaklı çevir."
        return await self.generate(system_prompt=system, user_prompt=text, temperature=0.3)
        
    async def pronunciation_feedback(self, tech_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        import os
        import json
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "coach.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            system = f.read()
            
        score = tech_data.get("overall_score", 0)
        strictness_directive = ""
        if score < 50:
            strictness_directive = "DİKKAT: Kullanıcının genel skoru çok düşük (50'nin altında). Kesinlikle övücü veya 'harika' gibi kelimeler kullanma. Tamamen ciddi ve eksik odaklı ol."
        elif score < 70:
            strictness_directive = "DİKKAT: Kullanıcının skoru orta seviyenin altında. Fazla iyimser olma, gelişmesi gereken yerlere net şekilde odaklan."
        elif score >= 90:
            strictness_directive = "DİKKAT: Kullanıcının skoru çok yüksek. Ufak tefek hatalar varsa abartma, hakkını ver."

        user_prompt = f"""
{strictness_directive}

[KULLANICI VERİLERİ]
- Toplam Seans: {context.get('total_sessions', 0)}
- Geçmiş Hedefleri: {json.dumps(context.get('past_goals', []), ensure_ascii=False)}
- Son Yorumların Özeti: {json.dumps(context.get('compressed_history', []), ensure_ascii=False)}

[BU KAYIT İÇİN TEKNİK ANALİZ VERİSİ]
- Overall Score: {score}
- Transcript (Kullanıcının okuduğu): {tech_data.get('transcript', '')}
- Expected (Okuması gereken): {tech_data.get('expected', '')}
- Accuracy: %{tech_data.get('accuracy', 0)}
- Fluency: %{tech_data.get('fluency', 0)}
- Rhythm: %{tech_data.get('rhythm', 0)}
- Stress: %{tech_data.get('stress', 0)}
- Intonation: %{tech_data.get('intonation', 0)}
- Confidence: %{tech_data.get('confidence', 0)}
- Phonemes (Hata Oranları): {json.dumps(tech_data.get('phonemes', {}))}
- Kelime Analizi: {json.dumps(tech_data.get('words', []), ensure_ascii=False)}
"""
        return await self.generate_json(system_prompt=system, user_prompt=user_prompt)
