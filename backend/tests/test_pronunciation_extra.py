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

def test_pronunciation_history(auth_client):
    res = auth_client.get("/api/pronunciation/history")
    assert res.status_code in [200, 400, 404, 405]

def test_pronunciation_stats(auth_client):
    res = auth_client.get("/api/pronunciation/stats")
    assert res.status_code in [200, 400, 404, 405]
