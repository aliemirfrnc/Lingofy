import json
import threading
import time
from collections import OrderedDict
from pathlib import Path

_LOCK = threading.Lock()
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

class TTLLRUCache:
    def __init__(self, name: str, max_size: int = 1000, ttl_seconds: int = 604800): # 7 days
        self.name = name
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict[str, dict] = OrderedDict()
        self.lock = threading.Lock()
        self._load()

    def _path(self) -> Path:
        return _DATA_DIR / f"{self.name}.json"

    def _load(self):
        path = self._path()
        if not path.exists():
            return
        try:
            with _LOCK:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            
            now = time.time()
            with self.lock:
                for k, v in data.items():
                    if isinstance(v, dict) and "timestamp" in v and "value" in v:
                        if now - v["timestamp"] < self.ttl_seconds:
                            self.cache[k] = v
                    else:
                        self.cache[k] = {"timestamp": now, "value": v}
        except Exception:
            pass

    def save(self):
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        path = self._path()
        
        with self.lock:
            now = time.time()
            keys_to_delete = [k for k, v in self.cache.items() if now - v["timestamp"] >= self.ttl_seconds]
            for k in keys_to_delete:
                del self.cache[k]
            data = dict(self.cache)

        with _LOCK:
            tmp_path = path.with_suffix(".tmp")
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            tmp_path.replace(path)

    def get(self, key: str, default=None):
        with self.lock:
            if key not in self.cache:
                return default
            
            item = self.cache[key]
            if time.time() - item["timestamp"] >= self.ttl_seconds:
                del self.cache[key]
                return default
            
            self.cache.move_to_end(key)
            return item["value"]

    def set(self, key: str, value):
        with self.lock:
            self.cache[key] = {"timestamp": time.time(), "value": value}
            self.cache.move_to_end(key)
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)
                
    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None

    def __getitem__(self, key: str):
        val = self.get(key)
        if val is None:
            raise KeyError(key)
        return val
        
    def __setitem__(self, key: str, value):
        self.set(key, value)

_caches: dict[str, TTLLRUCache] = {}
_caches_lock = threading.Lock()

def get_cache(name: str, max_size: int = 1000, ttl_seconds: int = 604800) -> TTLLRUCache:
    with _caches_lock:
        if name not in _caches:
            _caches[name] = TTLLRUCache(name, max_size, ttl_seconds)
        return _caches[name]

def load(name: str) -> TTLLRUCache:
    return get_cache(name)

def save(name: str, dummy_data=None) -> None:
    cache = get_cache(name)
    cache.save()