from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel

class AIProvider(ABC):
    @abstractmethod
    async def generate_json(self, system_prompt: str, user_prompt: str, schema: Type[BaseModel] | None = None, temperature: float = 0.4) -> Dict[str, Any]:
        """Generates structured JSON output based on an optional Pydantic schema."""
        pass

    @abstractmethod
    async def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """Generates plain text output."""
        pass

    @abstractmethod
    async def transcribe_audio(self, audio_path: str) -> str:
        """Transcribes audio file to text."""
        pass
