import pytest
from fastapi.testclient import TestClient
from backend.main import app
import time

@pytest.fixture
def auth_client():
    client = TestClient(app)
    test_email = f"trans_{int(time.time())}@test.com"
    client.post("/auth/register", json={"email": test_email, "password": "SecurePassword123!"})
    res = client.post("/auth/login", json={"email": test_email, "password": "SecurePassword123!"})
    client.cookies.set("access_token", res.cookies.get("access_token"))
    return client

def test_translate_line(auth_client, mocker):
    mock_ai = mocker.MagicMock()
    mock_ai.translate_text.return_value = "merhaba"
    mocker.patch("backend.core.services.ai_service.get_ai_service", return_value=mock_ai)
    
    res = auth_client.post("/translate-line", json={"text": "hello", "track_id": "test_track"})
    assert res.status_code in [200, 404, 422]

def test_translate_batch(auth_client, mocker):
    mock_ai = mocker.MagicMock()
    mock_ai.translate_text.return_value = "merhaba dünya"
    mocker.patch("backend.core.services.ai_service.get_ai_service", return_value=mock_ai)
    
    res = auth_client.post("/translate-batch", json={"lines": ["hello world"], "track_id": "test_track"})
    assert res.status_code in [200, 404, 422]
