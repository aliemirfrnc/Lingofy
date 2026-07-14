import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def auth_setup(mocker):
    from backend.core.auth import _create_access_token
    token = _create_access_token(1, "test@test.com")
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield

def test_whisper_failure_fallback(mocker):
    # STT Exception should fallback to expected_text
    mocker.patch("backend.routes.pronunciation.get_user_context", return_value={
        "avg_score": 80, "total_sessions": 10, "total_xp": 100, "level": "Beginner",
        "streak": 5, "recent_ai_comments": [], "past_goals": []
    })
    
    mock_stt = AsyncMock()
    mock_stt.transcribe_audio.side_effect = Exception("Whisper API Down")
    mocker.patch("backend.core.providers.ai_factory.get_stt_provider", return_value=mock_stt)
    
    # Mock AI feedback to return a simple dict
    mocker.patch("backend.routes.pronunciation.generate_ai_feedback", return_value={
        "summary": "AI is working",
        "strengths": [], "weaknesses": [], "suggestions": [], "next_goal": ""
    })
    
    # Mock DB functions
    conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    conn.cursor.return_value = cursor
    mocker.patch("backend.routes.pronunciation.get_conn", return_value=conn)
    mocker.patch("backend.routes.pronunciation.get_lock", MagicMock())
    
    # Upload a dummy audio
    files = {"audio": ("test.webm", b"dummy_audio_bytes", "audio/webm")}
    data = {"expected_text": "hello world"}
    
    res = client.post("/api/pronunciation/analyze", files=files, data=data)
    
    # Even if STT fails, it shouldn't crash, it should use expected_text as transcript
    assert res.status_code == 200
    json_resp = res.json()
    assert json_resp["accuracy"] == 100 # Because transcript == expected_text
    
def test_ai_timeout_fallback(mocker):
    mocker.patch("backend.routes.pronunciation.get_user_context", return_value={
        "avg_score": 80, "total_sessions": 10, "total_xp": 100, "level": "Beginner",
        "streak": 5, "recent_ai_comments": [], "past_goals": []
    })
    
    mock_stt = AsyncMock()
    mock_stt.transcribe_audio.return_value = "hello world"
    mocker.patch("backend.core.providers.ai_factory.get_stt_provider", return_value=mock_stt)
    
    # Generate AI Feedback fails
    mocker.patch("backend.routes.pronunciation.generate_ai_feedback", return_value={
            "summary": "",
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
            "next_goal": ""
    })
    
    conn = MagicMock()
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    conn.cursor.return_value = cursor
    mocker.patch("backend.routes.pronunciation.get_conn", return_value=conn)
    mocker.patch("backend.routes.pronunciation.get_lock", MagicMock())
    
    files = {"audio": ("test.webm", b"dummy_audio_bytes", "audio/webm")}
    data = {"expected_text": "hello world"}
    
    res = client.post("/api/pronunciation/analyze", files=files, data=data)
    
    assert res.status_code == 200
    json_resp = res.json()
    assert json_resp["summary"] == "İyi iş çıkardın!" # The fallback default
