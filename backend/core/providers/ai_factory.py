from backend.core.config import AI_PROVIDER
from backend.core.providers.ai_provider import AIProvider
from backend.core.providers.gemini_provider import GeminiProvider

def get_ai_provider() -> AIProvider:
    if AI_PROVIDER.lower() == "gemini":
        return GeminiProvider()
    
    # Fallback to Gemini if something else is specified but not implemented
    return GeminiProvider()
