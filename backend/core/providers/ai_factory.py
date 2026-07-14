from backend.core.config import AI_PROVIDER
from backend.core.providers.ai_provider import AIProvider
from backend.core.providers.stt_provider import SpeechToTextProvider
from backend.core.providers.openrouter_provider import OpenRouterProvider
from backend.core.providers.groq_whisper_provider import GroqWhisperProvider

def get_ai_provider() -> AIProvider:
    # Since we are completely migrating to OpenRouter for AI
    return OpenRouterProvider()

def get_stt_provider() -> SpeechToTextProvider:
    return GroqWhisperProvider()
