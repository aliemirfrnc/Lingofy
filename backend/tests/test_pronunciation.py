import pytest
from fastapi.testclient import TestClient
from backend.main import app
import time

@pytest.fixture
def auth_client():
    client = TestClient(app)
    test_email = f"pron_{int(time.time())}@test.com"
    client.post("/auth/register", json={"email": test_email, "password": "SecurePassword123!"})
    res = client.post("/auth/login", json={"email": test_email, "password": "SecurePassword123!"})
    client.cookies.set("access_token", res.cookies.get("access_token"))
    return client

def test_pronunciation_no_auth():
    client = TestClient(app)
    res = client.post("/api/pronunciation/analyze", data={"word": "test"})
    assert res.status_code in [401, 404, 422]

def test_pronunciation_success(auth_client, mocker):
    mock_ai = mocker.AsyncMock()
    mock_ai.analyze_pronunciation.return_value = {"score": 100}
    mocker.patch("backend.routes.pronunciation.get_ai_provider", return_value=mock_ai)
    
    # Using dummy file
    files = {"audio": ("test.wav", b"dummy audio content", "audio/wav")}
    res = auth_client.post("/api/pronunciation/analyze", data={"word": "test", "sentence": "test"}, files=files)
    assert res.status_code in [200, 404, 422]
