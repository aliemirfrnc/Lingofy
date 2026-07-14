import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import logging

logger = logging.getLogger(__name__)

class LrclibService:
    _thread_local = threading.local()
    _executor = ThreadPoolExecutor(max_workers=4)
    HEADERS = {"User-Agent": "Lingofy/1.0"}
    TIMEOUT = 15
    _LRC_TIME_RE = re.compile(r"\[(\d+):(\d+(?:\.\d+)?)\]")

    @classmethod
    def _get_session(cls) -> requests.Session:
        if not hasattr(cls._thread_local, "session"):
            s = requests.Session()
            s.headers.update(cls.HEADERS)
            cls._thread_local.session = s
        return cls._thread_local.session

    @staticmethod
    def _parse_plain(raw_text: str) -> list[str]:
        lines = [line.strip() for line in raw_text.split("\n")]
        return [line for line in lines if line]

    @classmethod
    def _parse_synced(cls, raw_text: str) -> list[dict]:
        result = []
        for line in raw_text.split("\n"):
            line = line.strip()
            if not line:
                continue
            match = cls._LRC_TIME_RE.match(line)
            if not match:
                continue
            minutes, seconds = match.groups()
            time_sec = int(minutes) * 60 + float(seconds)
            text = line[match.end():].strip()
            if text:
                result.append({"time": time_sec, "text": text})
        return result

    @classmethod
    def _extract(cls, data: dict) -> dict | None:
        synced_raw = data.get("syncedLyrics")
        plain_raw = data.get("plainLyrics")

        if synced_raw:
            synced = cls._parse_synced(synced_raw)
            if synced:
                return {"lyrics": [item["text"] for item in synced], "synced": synced}

        if plain_raw:
            plain = cls._parse_plain(plain_raw)
            if plain:
                return {"lyrics": plain, "synced": None}

        return None

    @classmethod
    def _fetch_get(cls, track: str, artist: str, error_flag: list) -> dict | None:
        max_retries = 2
        for attempt in range(max_retries):
            try:
                resp = cls._get_session().get(
                    "https://lrclib.net/api/get",
                    params={"track_name": track, "artist_name": artist},
                    timeout=cls.TIMEOUT,
                )
                if resp.status_code == 200:
                    return cls._extract(resp.json())
                elif resp.status_code == 404:
                    return None
                elif resp.status_code == 429:
                    retry_after = resp.headers.get("Retry-After")
                    sleep_time = float(retry_after) if retry_after else 1.0
                    import time
                    time.sleep(sleep_time)
                    continue
                    
                resp.raise_for_status()
            except (requests.RequestException, ValueError, TypeError) as e:
                logger.warning(f"LRCLIB GET ERROR on attempt {attempt+1}: {repr(e)}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)
                else:
                    error_flag.append(True)
        return None

    @classmethod
    def _fetch_search(cls, query: str, error_flag: list) -> dict | None:
        max_retries = 2
        for attempt in range(max_retries):
            try:
                resp = cls._get_session().get(
                    "https://lrclib.net/api/search",
                    params={"q": query},
                    timeout=cls.TIMEOUT,
                )
                if resp.status_code == 200:
                    results = resp.json()
                    if results:
                        return cls._extract(results[0])
                    return None
                elif resp.status_code == 429:
                    retry_after = resp.headers.get("Retry-After")
                    sleep_time = float(retry_after) if retry_after else 1.0
                    import time
                    time.sleep(sleep_time)
                    continue
                    
                resp.raise_for_status()
            except (requests.RequestException, ValueError, TypeError) as e:
                logger.warning(f"LRCLIB SEARCH ERROR on attempt {attempt+1}: {repr(e)}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)
                else:
                    error_flag.append(True)
        return None

    @classmethod
    def fetch_lyrics(cls, track: str, artist: str) -> tuple[dict | None, bool]:
        """İkinci eleman: ağ/timeout kaynaklı bir hata olup olmadığı.
        True ise 502 (tekrar denenebilir), False ise gerçekten sonuç yok (404)."""
        query = f"{track} {artist}".strip()
        error_flag: list = []
        futures = []

        if artist:
            futures.append(cls._executor.submit(cls._fetch_get, track, artist, error_flag))
        futures.append(cls._executor.submit(cls._fetch_search, query, error_flag))

        for future in as_completed(futures):
            result = future.result()
            if result:
                return result, False

        return None, len(error_flag) > 0

    @classmethod
    def warmup(cls, workers: int = 2) -> None:
        def _warm(_):
            try:
                cls._get_session().get(
                    "https://lrclib.net/api/search",
                    params={"q": "warmup"},
                    timeout=cls.TIMEOUT,
                )
            except requests.RequestException:
                pass

        list(cls._executor.map(_warm, range(workers)))
