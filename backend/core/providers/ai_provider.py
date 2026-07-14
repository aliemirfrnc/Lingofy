from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, AsyncGenerator
from pydantic import BaseModel

class AIProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """Generates plain text output."""
        pass

    @abstractmethod
    async def generate_json(self, system_prompt: str, user_prompt: str, schema: Type[BaseModel] | None = None, temperature: float = 0.4) -> Dict[str, Any]:
        """Generates structured JSON output."""
        pass

    @abstractmethod
    async def stream(self, system_prompt: str, messages: List[Dict[str, str]], temperature: float = 0.7) -> AsyncGenerator[str, None]:
        """Streams response for chat applications."""
        pass

    @abstractmethod
    async def chat(self, system_prompt: str, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Full response chat generation."""
        pass
        
    @abstractmethod
    async def summarize(self, text: str) -> str:
        pass
        
    @abstractmethod
    async def translate(self, text: str) -> str:
        pass
        
    @abstractmethod
    async def pronunciation_feedback(self, tech_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        pass
