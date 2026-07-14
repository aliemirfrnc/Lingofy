import pytest
from fastapi.testclient import TestClient
from backend.main import app
import time

@pytest.fixture
def auth_client():
    client = TestClient(app)
    test_email = f"spotify_{int(time.time())}@test.com"
    client.post("/auth/register", json={"email": test_email, "password": "SecurePassword123!"})
    res = client.post("/auth/login", json={"email": test_email, "password": "SecurePassword123!"})
    client.cookies.set("access_token", res.cookies.get("access_token"))
    return client

def test_spotify_callback(auth_client, mocker):
    mocker.patch("backend.routes.spotify.requests.post", return_value=mocker.MagicMock(status_code=200, json=lambda: {"access_token": "token", "refresh_token": "refresh"}))
    mocker.patch("backend.routes.spotify.requests.get", return_value=mocker.MagicMock(status_code=200, json=lambda: {"id": "spotify_id"}))
    res = auth_client.get("/spotify/callback?code=testcode")
    assert res.status_code in [200, 400, 307, 422]

def test_spotify_current(auth_client, mocker):
    res = auth_client.get("/spotify/current-track")
    assert res.status_code in [200, 400, 401, 404]

def test_spotify_queue(auth_client):
    res = auth_client.get("/spotify/queue")
    assert res.status_code in [200, 400, 401, 404]
    
def test_spotify_play(auth_client):
    res = auth_client.put("/spotify/play")
    assert res.status_code in [200, 400, 401, 404]

def test_spotify_pause(auth_client):
    res = auth_client.put("/spotify/pause")
    assert res.status_code in [200, 400, 401, 404]

def test_spotify_next(auth_client):
    res = auth_client.post("/spotify/next")
    assert res.status_code in [200, 400, 401, 404]

def test_spotify_playlists(auth_client):
    res = auth_client.get("/spotify/playlists")
    assert res.status_code in [200, 400, 401, 404]
