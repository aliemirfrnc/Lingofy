import pytest
from fastapi.testclient import TestClient
from backend.main import app
import time

@pytest.fixture
def auth_client():
    client = TestClient(app)
    test_email = f"lyrics_test_{int(time.time())}@test.com"
    client.post("/auth/register", json={"email": test_email, "password": "SecurePassword123!"})
    res = client.post("/auth/login", json={"email": test_email, "password": "SecurePassword123!"})
    client.cookies.set("access_token", res.cookies.get("access_token"))
    return client

def test_get_lyrics_cache_miss_success(auth_client, mocker):
    mocker.patch("backend.routes.lyrics.LrclibService.fetch_lyrics", return_value=({"lyrics": ["test"], "source": "LRCLIB"}, False))
    res = auth_client.get("/lyrics?track=Test&artist=Test")
    assert res.status_code == 200
    assert "lyrics" in res.json()

def test_get_lyrics_cache_hit(auth_client, mocker):
    mocker.patch("backend.routes.lyrics._cache", {"test::test": {"lyrics": ["hit"]}})
    res = auth_client.get("/lyrics?track=Test&artist=Test")
    assert res.status_code == 200
    assert "hit" in res.json()["lyrics"]

def test_get_lyrics_network_error(auth_client, mocker):
    mocker.patch("backend.routes.lyrics._cache", {})
    mocker.patch("backend.routes.lyrics.LrclibService.fetch_lyrics", return_value=(None, True))
    res = auth_client.get("/lyrics?track=TestErr&artist=TestErr")
    assert res.status_code == 502

def test_get_lyrics_not_found(auth_client, mocker):
    mocker.patch("backend.routes.lyrics._cache", {})
    mocker.patch("backend.routes.lyrics.LrclibService.fetch_lyrics", return_value=(None, False))
    res = auth_client.get("/lyrics?track=NotFound&artist=NotFound")
    assert res.status_code == 404
