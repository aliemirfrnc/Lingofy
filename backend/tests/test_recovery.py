import pytest
import asyncio
from backend.core.cache_store import get_cache
from backend.core.services.ai_service import get_ai_service
from backend.core.services.dictionary_service import DictionaryService
from httpx import ReadTimeout

@pytest.mark.asyncio
async def test_recovery_cache_wipe(mocker):
    # Simulate caching something
    cache = get_cache("test_recovery", ttl_seconds=100)
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"
    
    # Simulate system crash / cache wipe
    cache.cache.clear()
    
    # Should not crash, just return None
    assert cache.get("key1") is None
    
    # Should be able to set again perfectly
    cache.set("key1", "value2")
    assert cache.get("key1") == "value2"

@pytest.mark.asyncio
async def test_recovery_dictionary_api_down(mocker):
    # Simulate Dictionary API completely down (Timeout)
    mocker.patch("httpx.AsyncClient.get", side_effect=ReadTimeout("Dictionary API is down"))
    
    res = await DictionaryService.get_word_definition("apple")
    
    # The application should handle this gracefully and return fallback dictionary without crashing the whole event loop
    assert res is not None
    assert res["definition"] == ""
    assert res["part_of_speech"] == ""

@pytest.mark.asyncio
async def test_recovery_ai_circuit_breaker(mocker):
    # Trip the circuit breaker forcefully
    ai = get_ai_service()
    
    for _ in range(6):
        ai.groq.circuit_breaker.record_failure()
            
    assert not ai.groq.circuit_breaker.can_execute(), "Breaker should be OPEN"
    
    # Simulate time passing for Recovery (Half-Open)
    ai.groq.circuit_breaker.last_failure_time = 0
    
    # Should allow execution now (HALF-OPEN)
    assert ai.groq.circuit_breaker.can_execute(), "Breaker should have recovered to HALF-OPEN state"
