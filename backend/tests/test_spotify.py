import pytest
from fastapi.testclient import TestClient
from backend.main import app
import time

@pytest.fixture
def auth_client():
    client = TestClient(app)
    test_email = f"spotify_test_{int(time.time())}@test.com"
    client.post("/auth/register", json={"email": test_email, "password": "SecurePassword123!"})
    res = client.post("/auth/login", json={"email": test_email, "password": "SecurePassword123!"})
    client.cookies.set("access_token", res.cookies.get("access_token"))
    return client

def test_spotify_login(auth_client):
    res_token = auth_client.get("/spotify/connect-token")
    assert res_token.status_code == 200
    token = res_token.json()["connect_token"]
    
    res = auth_client.get(f"/spotify/login?token={token}", follow_redirects=False)
    assert res.status_code in [200, 307, 302, 303]

def test_spotify_callback_missing_code(auth_client):
    res = auth_client.get("/spotify/callback")
    assert res.status_code == 422

def test_spotify_current_track_no_token(auth_client):
    res = auth_client.get("/spotify/current-track")
    assert res.status_code == 404

def test_spotify_current_track_success(auth_client, mocker):
    mocker.patch("backend.routes.spotify._get_valid_token", return_value="fake_token")
    mock_resp = mocker.MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b"content"
    mock_resp.json.return_value = {"is_playing": True, "item": {"name": "Test", "artists": [{"name": "A"}], "duration_ms": 1000}}
    mocker.patch("backend.routes.spotify._spotify_request", return_value=mock_resp)
    
    res = auth_client.get("/spotify/current-track")
    assert res.status_code == 200
    assert res.json()["is_playing"] is True

def test_spotify_queue(auth_client, mocker):
    mocker.patch("backend.routes.spotify._get_valid_token", return_value="fake_token")
    mock_resp = mocker.MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"queue": [{"name": "Test", "artists": [{"name": "A"}]}]}
    mocker.patch("backend.routes.spotify._spotify_request", return_value=mock_resp)
    
    res = auth_client.get("/spotify/queue")
    assert res.status_code == 200
    assert res.json()["track_name"] == "Test"
