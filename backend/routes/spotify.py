import time
import uuid
from urllib.parse import urlencode

import requests
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from backend.core.config import (
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI,
    FRONTEND_URL,
)

router = APIRouter(prefix="/spotify")

SCOPE = "user-read-currently-playing user-read-playback-state user-modify-playback-state"

# session_id -> {access_token, refresh_token, expires_at}
_sessions: dict[str, dict] = {}


class CurrentTrackResponse(BaseModel):
    is_playing: bool
    track_name: str | None = None
    artist: str | None = None
    album_image: str | None = None
    progress_ms: int | None = None
    duration_ms: int | None = None


@router.get("/login")
def spotify_login():
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": SCOPE,
    }
    return RedirectResponse(f"https://accounts.spotify.com/authorize?{urlencode(params)}")


@router.get("/callback")
def spotify_callback(code: str = Query(...)):
    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": SPOTIFY_REDIRECT_URI,
            "client_id": SPOTIFY_CLIENT_ID,
            "client_secret": SPOTIFY_CLIENT_SECRET,
        },
    )

    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Spotify yetkilendirme başarısız.")

    data = resp.json()
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "expires_at": time.time() + data["expires_in"],
    }

    return RedirectResponse(f"{FRONTEND_URL}?spotify_session={session_id}")


def _get_valid_token(session_id: str) -> str:
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Spotify bağlantısı bulunamadı.")

    if time.time() >= session["expires_at"] - 30:
        resp = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": session["refresh_token"],
                "client_id": SPOTIFY_CLIENT_ID,
                "client_secret": SPOTIFY_CLIENT_SECRET,
            },
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Spotify oturumu yenilenemedi.")

        data = resp.json()
        session["access_token"] = data["access_token"]
        session["expires_at"] = time.time() + data["expires_in"]
        if "refresh_token" in data:
            session["refresh_token"] = data["refresh_token"]

    return session["access_token"]


@router.get("/current-track", response_model=CurrentTrackResponse)
def current_track(session_id: str = Query(...)):
    token = _get_valid_token(session_id)

    resp = requests.get(
        "https://api.spotify.com/v1/me/player/currently-playing",
        headers={"Authorization": f"Bearer {token}"},
    )

    if resp.status_code == 204 or not resp.content:
        return {"is_playing": False}

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Spotify verisi alınamadı.")

    data = resp.json()
    item = data.get("item")
    if not item:
        return {"is_playing": False}

    images = item.get("album", {}).get("images", [])

    return {
        "is_playing": data.get("is_playing", False),
        "track_name": item.get("name"),
        "artist": ", ".join(a["name"] for a in item.get("artists", [])),
        "album_image": images[0]["url"] if images else None,
        "progress_ms": data.get("progress_ms"),
        "duration_ms": item.get("duration_ms"),
    }


def _player_command(method: str, session_id: str, path: str) -> dict:
    token = _get_valid_token(session_id)
    resp = requests.request(
        method,
        f"https://api.spotify.com/v1/me/player/{path}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code not in (200, 204):
        raise HTTPException(
            status_code=resp.status_code,
            detail="Komut başarısız. Aktif bir Spotify cihazı açık mı?",
        )
    return {"status": "ok"}


@router.put("/play")
def play(session_id: str = Query(...)):
    return _player_command("PUT", session_id, "play")


@router.put("/pause")
def pause(session_id: str = Query(...)):
    return _player_command("PUT", session_id, "pause")


@router.post("/next")
def next_track(session_id: str = Query(...)):
    return _player_command("POST", session_id, "next")


@router.post("/previous")
def previous_track(session_id: str = Query(...)):
    return _player_command("POST", session_id, "previous")