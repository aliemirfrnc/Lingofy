import time
import asyncio
import logging
from groq import AsyncGroq
from backend.core.config import GROQ_API_KEY
from backend.core.providers.stt_provider import SpeechToTextProvider

logger = logging.getLogger(__name__)

class GroqWhisperProvider(SpeechToTextProvider):
    _instance = None

    def __new__(cls):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY bulunamadı! Lütfen .env dosyanızı kontrol edin.")
            
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = AsyncGroq(api_key=GROQ_API_KEY.strip())
        return cls._instance

    @property
    def client(self):
        return self._client

    async def transcribe_audio(self, audio_path: str) -> str:
        max_retries = 3
        backoff_times = [1, 2, 4]
        
        for attempt in range(max_retries):
            start_time = time.time()
            try:
                with open(audio_path, "rb") as file:
                    transcription = await self.client.audio.transcriptions.create(
                        file=(audio_path, file.read()),
                        model="whisper-large-v3",
                        response_format="text"
                    )
                latency = time.time() - start_time
                logger.info(f"[Groq Whisper] transcribe_audio | Latency: {latency:.2f}s")
                return transcription.strip()
                
            except Exception as e:
                latency = time.time() - start_time
                logger.warning(f"Attempt {attempt + 1} failed for transcribe_audio: {repr(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(backoff_times[attempt])
                else:
                    logger.error("All retries exhausted for STT transcribe_audio.")
                    raise
        return ""
