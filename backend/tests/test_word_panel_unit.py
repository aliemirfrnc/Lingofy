import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def auth_setup(mocker):
    from backend.core.auth import _create_access_token
    token = _create_access_token(1, "test@test.com")
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield

@pytest.fixture
def mock_db(mocker):
    conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    conn.cursor.return_value = cursor
    mocker.patch("backend.core.db.get_conn", return_value=conn)
    mocker.patch("backend.core.db.get_lock", MagicMock())
    mocker.patch("backend.core.services.subscription_service.SubscriptionService.consume_feature_atomic", return_value=(True, ""))
    return True

class DummyCache:
    def __init__(self, init_dict=None): self.d = init_dict or {}
    def get(self, k, default=None): return self.d.get(k, default)
    def set(self, k, v): self.d[k] = v
    def __setitem__(self, k, v): self.d[k] = v

def test_word_info_cache_hit(mocker, mock_db):
    mocker.patch("backend.routes.word_info._cache", DummyCache({"apple::i ate an apple": {
        "word": "apple",
        "turkish_meanings": ["elma"],
        "part_of_speech": "noun",
        "pronunciation": "/ˈæpəl/",
        "definition": "A fruit",
        "grammar_note": "",
        "synonyms": [],
        "antonyms": [],
        "examples": [],
        "collocations": [],
        "phrasal_verbs": [],
        "word_family": [],
        "syllables": "ap-ple",
        "contextual_meaning": "context",
        "ai_learning_tip": "tip"
    }}))
    
    res = client.post("/api/word-info", json={"word": "apple", "context_line": "I ate an apple"})
    assert res.status_code == 200
    assert res.json()["definition"] == "A fruit"

def test_word_info_ai_success(mocker, mock_db):
    mocker.patch("backend.routes.word_info._cache", DummyCache())
    
    mock_ai = AsyncMock()
    mock_ai.get_word_context.return_value = {
        "contextual_meaning": "context",
        "ai_learning_tip": "tip"
    }
    mocker.patch("backend.routes.word_info.get_ai_service", return_value=mock_ai)
    
    mocker.patch("backend.routes.word_info.DictionaryService.get_word_definition", return_value={"definition": "A smart fruit", "cefr_level": "A1", "part_of_speech": "noun"})
    mocker.patch("backend.routes.word_info.TranslationService.get_turkish_translation", return_value="akıllı meyve")
    
    res = client.post("/api/word-info", json={"word": "apple", "context_line": "I ate an apple"})
    assert res.status_code == 200
    assert res.json()["definition"] == "A smart fruit"
    assert res.json()["turkish_meanings"] == ["akıllı meyve"]

def test_word_info_ai_failure(mocker, mock_db):
    mocker.patch("backend.routes.word_info._cache", DummyCache())
    
    mock_ai = AsyncMock()
    mock_ai.get_word_context.side_effect = Exception("LLM Down")
    mocker.patch("backend.routes.word_info.get_ai_service", return_value=mock_ai)
    
    mocker.patch("backend.routes.word_info.DictionaryService.get_word_definition", return_value={"definition": "Bilgi alınamadı."})
    mocker.patch("backend.routes.word_info.TranslationService.get_turkish_translation", return_value="")
    
    res = client.post("/api/word-info", json={"word": "apple", "context_line": "I ate an apple"})
    assert res.status_code == 200
    assert res.json()["definition"] == "Bilgi alınamadı."

def test_word_favorite_toggle(mocker, mock_db):
    conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchone.return_value = [1] # Exists
    conn.execute.return_value = cursor
    mocker.patch("backend.routes.word_info.get_conn", return_value=conn)
    
    res = client.post("/api/words/favorite", json={"word": "apple"})
    assert res.status_code == 200
    assert res.json()["is_favorite"] is False

def test_word_memorize(mocker, mock_db):
    conn = MagicMock()
    cursor = MagicMock()
    cursor.rowcount = 1
    cursor.fetchone.return_value = [0, 5]
    conn.cursor.return_value = cursor
    mocker.patch("backend.routes.word_info.get_conn", return_value=conn)
    
    res = client.post("/api/words/memorize", json={"word": "apple"})
    assert res.status_code == 200
    assert res.json()["success"] is True
    assert res.json()["is_memorized"] is True

def test_word_review(mocker, mock_db):
    conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchone.return_value = [1, 2.5]
    conn.execute.return_value = cursor
    mocker.patch("backend.routes.word_info.get_conn", return_value=conn)
    
    res = client.post("/api/words/review", json={"word": "apple", "correct": True})
    assert res.status_code == 200
    assert res.json()["success"] is True
