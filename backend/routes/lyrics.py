import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


class SyncedLine(BaseModel):
    time: float
    text: str


class LyricsResponse(BaseModel):
    lyrics: list[str]
    synced: list[SyncedLine] | None = None
    source: str


_cache: dict[str, dict] = {}

HEADERS = {"User-Agent": "Lingofy/1.0"}
TIMEOUT = 10

_LRC_TIME_RE = re.compile(r"\[(\d+):(\d+(?:\.\d+)?)\]")


def _parse_plain(raw_text: str) -> list[str]:
    lines = [line.strip() for line in raw_text.split("\n")]
    return [line for line in lines if line]


def _parse_synced(raw_text: str) -> list[dict]:
    result = []
    for line in raw_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        match = _LRC_TIME_RE.match(line)
        if not match:
            continue
        minutes, seconds = match.groups()
        time_sec = int(minutes) * 60 + float(seconds)
        text = line[match.end():].strip()
        if text:
            result.append({"time": time_sec, "text": text})
    return result


def _extract(data: dict) -> dict | None:
    synced_raw = data.get("syncedLyrics")
    plain_raw = data.get("plainLyrics")

    if synced_raw:
        synced = _parse_synced(synced_raw)
        if synced:
            return {"lyrics": [item["text"] for item in synced], "synced": synced}

    if plain_raw:
        plain = _parse_plain(plain_raw)
        if plain:
            return {"lyrics": plain, "synced": None}

    return None


def _fetch_get(track: str, artist: str) -> dict | None:
    try:
        resp = requests.get(
            "https://lrclib.net/api/get",
            params={"track_name": track, "artist_name": artist},
            timeout=TIMEOUT,
            headers=HEADERS,
        )
        if resp.status_code == 200:
            return _extract(resp.json())
    except requests.RequestException as e:
        print("LYRICS GET ERROR:", repr(e))
    return None


def _fetch_search(query: str) -> dict | None:
    try:
        resp = requests.get(
            "https://lrclib.net/api/search",
            params={"q": query},
            timeout=TIMEOUT,
            headers=HEADERS,
        )
        if resp.status_code == 200:
            results = resp.json()
            if results:
                return _extract(results[0])
    except requests.RequestException as e:
        print("LYRICS SEARCH ERROR:", repr(e))
    return None


def _fetch_parallel(track: str, artist: str) -> dict | None:
    query = f"{track} {artist}".strip()
    tasks = []

    with ThreadPoolExecutor(max_workers=2) as pool:
        if artist:
            tasks.append(pool.submit(_fetch_get, track, artist))
        tasks.append(pool.submit(_fetch_search, query))

        for future in as_completed(tasks):
            result = future.result()
            if result:
                return result

    return None


@router.get("/lyrics", response_model=LyricsResponse)
def get_lyrics(
    track: str = Query(...),
    artist: str = Query(""),
):
    cache_key = f"{track.lower()}::{artist.lower()}"
    if cache_key in _cache:
        return {**_cache[cache_key], "source": "LRCLIB (cache)"}

    data = _fetch_parallel(track, artist)

    if not data:
        raise HTTPException(status_code=404, detail="Bu şarkı için söz bulunamadı.")

    _cache[cache_key] = data
    return {**data, "source": "LRCLIB"}