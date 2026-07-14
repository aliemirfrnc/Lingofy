import pytest
import requests
from fastapi import HTTPException
from unittest.mock import MagicMock
from backend.routes.spotify import _spotify_request, _get_valid_token, NO_ACTIVE_DEVICE_MESSAGE, _player_command

def test_spotify_request_retry(mocker):
    mock_request = mocker.patch("backend.routes.spotify.requests.request")
    
    # 1st attempt: 429 Rate Limit
    resp_429 = MagicMock(spec=requests.Response)
    resp_429.status_code = 429
    resp_429.headers = {"Retry-After": "0.1"}
    
    # 2nd attempt: 200 Success
    resp_200 = MagicMock(spec=requests.Response)
    resp_200.status_code = 200
    
    mock_request.side_effect = [resp_429, resp_200]
    
    res = _spotify_request("GET", "url")
    assert res.status_code == 200
    assert mock_request.call_count == 2

def test_spotify_request_timeout(mocker):
    mock_request = mocker.patch("backend.routes.spotify.requests.request")
    mock_request.side_effect = requests.RequestException("Network Error")
    
    with pytest.raises(HTTPException) as exc:
        _spotify_request("GET", "url")
        
    assert exc.value.status_code == 502
    assert "Spotify servisine şu anda ulaşılamıyor" in exc.value.detail

def test_get_valid_token_refresh(mocker):
    # Mocking db functions
    mocker.patch("backend.routes.spotify._get_spotify_row", return_value=("access_old", "refresh_tok", 0)) # Expired token
    
    mock_request = mocker.patch("backend.routes.spotify.requests.request")
    resp_200 = MagicMock(spec=requests.Response)
    resp_200.status_code = 200
    resp_200.json.return_value = {"access_token": "access_new", "expires_in": 3600}
    mock_request.return_value = resp_200
    
    mocker.patch("backend.routes.spotify._save_spotify_tokens")
    
    new_token = _get_valid_token(1)
    assert new_token == "access_new"
    
def test_get_valid_token_invalid_refresh(mocker):
    mocker.patch("backend.routes.spotify._get_spotify_row", return_value=("access_old", "refresh_tok", 0))
    
    mock_request = mocker.patch("backend.routes.spotify.requests.request")
    resp_400 = MagicMock(spec=requests.Response)
    resp_400.status_code = 400
    mock_request.return_value = resp_400
    
    mocker.patch("backend.routes.spotify._delete_spotify_tokens")
    
    with pytest.raises(HTTPException) as exc:
        _get_valid_token(1)
        
    assert exc.value.status_code == 404
    assert "Spotify yetkisi iptal edilmiş" in exc.value.detail

def test_player_command_no_device(mocker):
    mocker.patch("backend.routes.spotify._get_valid_token", return_value="token")
    mock_req = mocker.patch("backend.routes.spotify._spotify_request")
    
    resp_404 = MagicMock(spec=requests.Response)
    resp_404.status_code = 404
    resp_404.json.return_value = {"error": {"reason": "NO_ACTIVE_DEVICE"}}
    mock_req.return_value = resp_404
    
    with pytest.raises(HTTPException) as exc:
        _player_command("PUT", 1, "play")
        
    assert exc.value.status_code == 404
    assert exc.value.detail == NO_ACTIVE_DEVICE_MESSAGE
