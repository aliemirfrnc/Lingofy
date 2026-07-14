import pytest
import os
import asyncio
from backend.core.providers.groq_provider import GroqProvider
from backend.core.providers.openrouter_provider import OpenRouterProvider
from backend.core.services.dictionary_service import DictionaryService

@pytest.mark.asyncio
async def test_groq_real_call():
    if not os.getenv("GROQ_API_KEY"):
        pytest.skip("GROQ_API_KEY not found")
        
    groq = GroqProvider()
    result = await groq.generate(
        system_prompt="Sen bir asistansın.",
        user_prompt="Sadece 'success' yaz.",
        temperature=0.1
    )
    assert isinstance(result, str)
    assert "success" in result.lower()

@pytest.mark.asyncio
async def test_openrouter_real_call():
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY not found")
        
    op = OpenRouterProvider()
    result = await op.generate(
        system_prompt="You are a helpful assistant.",
        user_prompt="Say the word 'Banana' and nothing else.",
        temperature=0.1
    )
    assert isinstance(result, str)
    assert "banana" in result.lower()

@pytest.mark.asyncio
async def test_dictionary_api_real_call():
    result = await DictionaryService.get_word_definition("apple")
    assert isinstance(result, dict)
    assert "part_of_speech" in result
    assert "definition" in result
    assert result["part_of_speech"] == "noun"
    assert result["definition"] != ""
