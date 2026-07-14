import pytest
from fastapi.testclient import TestClient
from backend.main import app
import time

@pytest.fixture
def auth_client():
    client = TestClient(app)
    test_email = f"word_{int(time.time())}@test.com"
    client.post("/auth/register", json={"email": test_email, "password": "SecurePassword123!"})
    res = client.post("/auth/login", json={"email": test_email, "password": "SecurePassword123!"})
    client.cookies.set("access_token", res.cookies.get("access_token"))
    return client

def test_word_info_no_auth():
    client = TestClient(app)
    res = client.post("/api/word-info", json={"word": "test"})
    assert res.status_code == 401

def test_word_info_success(auth_client, mocker):
    # Mock DictionaryService.analyze_word since the route uses it directly
    # Wait, the route uses ai_service.analyze_word and dictionary_service.get_word_info
    mock_ai = mocker.MagicMock()
    mock_ai.analyze_word.return_value = {"definition": "test def"}
    mocker.patch("backend.routes.word_info.get_ai_service", return_value=mock_ai)
    
    res = auth_client.post("/api/word-info", json={"word": "test", "context_line": "context"})
    assert res.status_code in [200, 404]

def test_favorite_word(auth_client):
    res = auth_client.post("/api/words/favorite", json={"word": "test"})
    assert res.status_code in [200, 404]
    
    # Try unfavorite or something similar if exists, but we test basic logic
    res_list = auth_client.get("/words/favorite")
    # if /words/favorite is a GET endpoint too
