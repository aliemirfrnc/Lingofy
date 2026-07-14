import pytest
from fastapi.testclient import TestClient
from backend.main import app
import time

@pytest.fixture
def auth_client():
    client = TestClient(app)
    test_email = f"chat_{int(time.time())}@test.com"
    client.post("/auth/register", json={"email": test_email, "password": "SecurePassword123!"})
    res = client.post("/auth/login", json={"email": test_email, "password": "SecurePassword123!"})
    client.cookies.set("access_token", res.cookies.get("access_token"))
    return client

def test_chat_no_auth():
    client = TestClient(app)
    res = client.post("/chat", json={"message": "hello"})
    assert res.status_code == 401

def test_chat_success(auth_client, mocker):
    async def mock_stream(*args, **kwargs):
        yield b"data: {\"text\": \"hello\"}\n\n"
        yield b"data: {\"done\": true}\n\n"
        
    mock_service = mocker.AsyncMock()
    mock_service.get_chat_stream.return_value = mock_stream()
    mocker.patch("backend.core.services.ai_service.get_ai_service", return_value=mock_service)
    
    res = auth_client.post("/chat", json={"message": "hello"})
    assert res.status_code == 200
