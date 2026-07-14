import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def auth_setup():
    from backend.core.auth import _create_access_token
    token = _create_access_token(1, "test@test.com")
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield

class DummyCache:
    def __init__(self): self.d = {}
    def get(self, k, default=None): return self.d.get(k, default)
    def set(self, k, v): self.d[k] = v

def test_translation_cache_miss_and_success(mocker):
    mocker.patch("backend.routes.translate._cache", DummyCache())
    mocker.patch("backend.core.providers.groq_provider.GroqProvider.generate", return_value="merhaba")
    
    res = client.post("/translate-line", json={"text": "hello"})
    
    assert res.status_code == 200
    assert res.json()["translation"] == "merhaba"

def test_translation_cache_hit(mocker):
    mock_tc = AsyncMock()
    mock_tc.return_value = ("merhaba_cached", False)
    mocker.patch("backend.routes.translate._translate_cached", new=mock_tc)
    
    res = client.post("/translate-line", json={"text": "hello"})
    
    assert res.status_code == 200
    assert res.json()["translation"] == "merhaba_cached"

def test_translation_empty_text():
    res = client.post("/translate-line", json={"text": "   "})
    assert res.status_code == 200
    assert res.json()["translation"] == ""

def test_translation_fallback(mocker):
    mocker.patch("backend.routes.translate._cache", DummyCache())
    mocker.patch("backend.core.providers.groq_provider.GroqProvider.generate", side_effect=Exception("Groq failed"))
    mocker.patch("backend.core.services.dictionary_service.TranslationService.get_turkish_translation", return_value="merhaba (fallback)")
    
    res = client.post("/translate-line", json={"text": "hello"})
    
    assert res.status_code == 200
    assert res.json()["translation"] == "merhaba (fallback)"
