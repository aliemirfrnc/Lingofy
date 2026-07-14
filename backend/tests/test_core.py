import pytest
from fastapi.testclient import TestClient
from backend.main import app

def test_health():
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200

def test_cache_hit_and_miss():
    from backend.core.cache_store import get_cache
    cache = get_cache("test_cache")
    cache.set("test_key", {"data": "test"})
    assert cache.get("test_key") == {"data": "test"}
    assert cache.get("missing") is None
