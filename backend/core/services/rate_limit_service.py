import time
import logging
import sqlite3
import redis
from fastapi import Request, HTTPException
from backend.core.db import get_conn, get_lock, init_db
from backend.core.cache_store import redis_client

logger = logging.getLogger(__name__)

def check_rate_limit(request: Request, limit: int = 100, window: int = 60, scope: str = "global"):
    """
    Rate Limiter that utilizes Redis if available, 
    otherwise falls back to the SQLite table for local development.
    """
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    key = f"{ip}:{scope}"
    if redis_client:
        key = f"rate_limit:{key}"
        try:
            current = redis_client.get(key)
            if current and int(current) >= limit:
                raise HTTPException(status_code=429, detail="Çok fazla istek gönderdiniz. Lütfen daha sonra tekrar deneyin.")
            
            pipe = redis_client.pipeline()
            pipe.incr(key)
            if not current:
                pipe.expire(key, window)
            pipe.execute()
            return
        except redis.RedisError as e:
            logger.error(f"Redis rate limit error, falling back to DB: {e}")

    # Fallback to SQLite
    conn = get_conn()
    with get_lock():
        try:
            cur = conn.execute("SELECT request_count, reset_at FROM rate_limits WHERE ip_address = ?", (key,))
        except sqlite3.OperationalError as exc:
            if "no such table" not in str(exc):
                raise
            # Supports application instances initialized without a lifespan (e.g. unit clients).
            init_db()
            cur = conn.execute("SELECT request_count, reset_at FROM rate_limits WHERE ip_address = ?", (key,))
        row = cur.fetchone()
        
        if not row:
            conn.execute("INSERT INTO rate_limits (ip_address, request_count, reset_at) VALUES (?, 1, ?)", (key, now + window))
        else:
            count, reset_at = row
            if now > reset_at:
                conn.execute("UPDATE rate_limits SET request_count = 1, reset_at = ? WHERE ip_address = ?", (now + window, key))
            else:
                if count >= limit:
                    conn.commit()
                    raise HTTPException(status_code=429, detail="Çok fazla istek gönderdiniz. Lütfen daha sonra tekrar deneyin.")
                else:
                    conn.execute("UPDATE rate_limits SET request_count = request_count + 1 WHERE ip_address = ?", (key,))
        conn.commit()
