import pytest
import asyncio
import httpx
from unittest.mock import AsyncMock, MagicMock
from backend.core.providers.groq_provider import GroqProvider
from backend.core.providers.openrouter_provider import OpenRouterProvider
from backend.core.providers.circuit_breaker import CircuitBreaker

@pytest.fixture
def reset_providers():
    # Reset singleton instances
    GroqProvider._instance = None
    OpenRouterProvider._instance = None

@pytest.mark.asyncio
async def test_groq_retry_and_rate_limit(reset_providers, mocker):
    provider = GroqProvider()
    provider.circuit_breaker = CircuitBreaker()
    
    mock_post = AsyncMock()
    # 1st call: 429 Rate Limit
    resp_429 = MagicMock(spec=httpx.Response)
    resp_429.status_code = 429
    resp_429.headers = {"Retry-After": "0.1"}
    
    # 2nd call: 503 Server Error
    resp_503 = httpx.Response(503, request=httpx.Request("POST", "url"))
    
    # 3rd call: 200 Success
    resp_200 = httpx.Response(200, json={
        "usage": {"prompt_tokens": 10, "completion_tokens": 10},
        "choices": [{"message": {"content": "success"}}]
    }, request=httpx.Request("POST", "url"))
    
    # Side effect for mock_post
    mock_post.side_effect = [resp_429, httpx.HTTPStatusError("503", request=resp_503.request, response=resp_503), resp_200]
    mocker.patch.object(provider.client, "post", mock_post)
    
    # Should succeed on the 3rd attempt
    res = await provider._execute_with_retry("test_method", {"model": "test"})
    assert res.status_code == 200
    assert provider.metrics["retries"] == 2
    assert provider.metrics["successes"] == 1

@pytest.mark.asyncio
async def test_groq_timeout(reset_providers, mocker):
    provider = GroqProvider()
    
    mock_post = AsyncMock()
    mock_post.side_effect = httpx.ReadTimeout("Timeout")
    mocker.patch.object(provider.client, "post", mock_post)
    
    with pytest.raises(httpx.ReadTimeout, match="Timeout"):
        await provider._execute_with_retry("test_method", {})
        
    assert provider.metrics["failures"] == 1

@pytest.mark.asyncio
async def test_groq_json_repair(reset_providers, mocker):
    provider = GroqProvider()
    
    mock_execute = AsyncMock()
    # Return broken JSON
    broken_resp = httpx.Response(200, json={
        "choices": [{"message": {"content": "{ 'bad': 'json', }"}}]
    }, request=httpx.Request("POST", "url"))
    
    mock_execute.return_value = broken_resp
    mocker.patch.object(provider, "_execute_with_retry", mock_execute)
    
    res = await provider.generate_json("sys", "user")
    assert res == {"bad": "json"}

@pytest.mark.asyncio
async def test_groq_invalid_json_fallback(reset_providers, mocker):
    provider = GroqProvider()
    
    mock_execute = AsyncMock()
    # Unrepairable JSON
    bad_resp = httpx.Response(200, json={
        "choices": [{"message": {"content": "not a json at all"}}]
    }, request=httpx.Request("POST", "url"))
    
    mock_execute.return_value = bad_resp
    mocker.patch.object(provider, "_execute_with_retry", mock_execute)
    
    with pytest.raises(ValueError, match="Geçersiz JSON formatı"):
        await provider.generate_json("sys", "user")

@pytest.mark.asyncio
async def test_openrouter_circuit_breaker(reset_providers, mocker):
    provider = OpenRouterProvider()
    
    mock_post = AsyncMock()
    resp_500 = httpx.Response(500, request=httpx.Request("POST", "url"))
    mock_post.side_effect = httpx.HTTPStatusError("500", request=resp_500.request, response=resp_500)
    mocker.patch.object(provider.client, "post", mock_post)
    
    # Exhaust retries on first request
    with pytest.raises(httpx.HTTPStatusError):
        await provider._execute_with_retry("test", {})
    
    # Need 5 consecutive failures to open circuit
    for _ in range(4):
        with pytest.raises(httpx.HTTPStatusError):
            await provider._execute_with_retry("test", {})
            
    # Now circuit should be OPEN
    with pytest.raises(Exception, match="Circuit Breaker OPEN"):
        await provider._execute_with_retry("test", {})
