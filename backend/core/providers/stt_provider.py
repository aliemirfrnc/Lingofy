from abc import ABC, abstractmethod

class SpeechToTextProvider(ABC):
    @abstractmethod
    async def transcribe_audio(self, audio_path: str) -> str:
        """Transcribes audio file to text."""
        pass
