from typing import Any, Dict, List, Type, AsyncGenerator
from pydantic import BaseModel
import logging
import time
from backend.core.events import EventBus
from backend.core.providers.openrouter_provider import OpenRouterProvider
from backend.core.providers.groq_provider import GroqProvider

logger = logging.getLogger(__name__)

class AIService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.openrouter = OpenRouterProvider()
            cls._instance.groq = GroqProvider()
        return cls._instance

    async def health_check(self):
        try:
            await self.groq.generate(system_prompt="health", user_prompt="health", temperature=0.0)
            logger.info("Groq Provider Health: OK")
        except Exception as e:
            logger.warning(f"Groq Provider Health: FAIL - {repr(e)}")
            
        try:
            await self.openrouter.generate(system_prompt="health", user_prompt="health", temperature=0.0)
            logger.info("OpenRouter Provider Health: OK")
        except Exception as e:
            logger.warning(f"OpenRouter Provider Health: FAIL - {repr(e)}")


    # 1. Word Info (Groq) - Temperature: 0.0
    async def get_word_context(self, system_prompt: str, user_prompt: str, schema: Type[BaseModel]) -> Dict[str, Any]:
        start_t = time.time()
        try:
            res = await self.groq.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema=schema,
                temperature=0.0
            )
            await EventBus.publish("AI_REQUEST_COMPLETED", {"provider": "groq", "latency": time.time()-start_t})
            return res
        except Exception as e:
            await EventBus.publish("AI_REQUEST_FAILED", {"provider": "groq", "error": str(e)})
            logger.warning(f"Groq get_word_context failed: {repr(e)}. Falling back to OpenRouter.")
            res = await self.openrouter.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema=schema,
                temperature=0.0
            )


    # 3. Chat (OpenRouter) - Temperature: 0.6
    async def get_chat_stream(self, system_prompt: str, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        return self.openrouter.stream(
            system_prompt=system_prompt,
            messages=messages,
            temperature=0.6
        )

    # 4. Pronunciation (OpenRouter) - Temperature: 0.3
    async def get_pronunciation_feedback(self, system_prompt: str, user_prompt: str, schema: Type[BaseModel] | None = None) -> Dict[str, Any]:
        if schema:
            return await self.openrouter.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema=schema,
                temperature=0.3
            )
        else:
            # Fallback to plain text if no schema
            res = await self.openrouter.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3
            )
            return {"feedback": res}

def get_ai_service() -> AIService:
    return AIService()
