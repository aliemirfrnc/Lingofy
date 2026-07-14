import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_register_rate_limit():
    email = "spam_test@example.com"
    
    # 1. Send 5 invalid registers to trigger rate limit (e.g., short password)
    for i in range(5):
        resp = client.post("/auth/register", json={"email": email, "password": "short"})
        assert resp.status_code == 400
        
    # 2. 6th attempt should be 429 Too Many Requests
    resp_locked = client.post("/auth/register", json={"email": email, "password": "ValidPassword123!"})
    assert resp_locked.status_code == 429
