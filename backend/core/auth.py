import hashlib
import os
import secrets
import time

import jwt

from backend.core.config import (
    JWT_ACCESS_TTL_SECONDS,
    JWT_REFRESH_TTL_SECONDS,
    JWT_SECRET,
)
from backend.core.db import get_conn, get_lock

JWT_ALGORITHM = "HS256"


from passlib.hash import argon2

def hash_password(password: str) -> str:
    return argon2.using(type="ID").hash(password)

def verify_password(password: str, stored: str) -> bool:
    try:
        return argon2.verify(password, stored)
    except Exception:
        return False


def create_user(email: str, password: str) -> int:
    conn = get_conn()
    with get_lock():
        cur = conn.execute(
            "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
            (email.lower().strip(), hash_password(password), time.time()),
        )
        conn.commit()
        return cur.lastrowid


def get_user_by_email(email: str):
    conn = get_conn()
    with get_lock():
        cur = conn.execute(
            "SELECT id, email, password_hash FROM users WHERE email = ?",
            (email.lower().strip(),),
        )
        return cur.fetchone()


def get_user_by_id(user_id: int):
    conn = get_conn()
    with get_lock():
        cur = conn.execute(
            "SELECT id, email, password_hash FROM users WHERE id = ?",
            (user_id,),
        )
        return cur.fetchone()


def _hash_refresh_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _create_access_token(user_id: int, email: str) -> str:
    now = time.time()
    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": now,
        "exp": now + JWT_ACCESS_TTL_SECONDS,
        "type": "access",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def _store_refresh_token(user_id: int, raw_token: str) -> None:
    now = time.time()
    token_hash = _hash_refresh_token(raw_token)
    conn = get_conn()
    with get_lock():
        conn.execute(
            "INSERT INTO refresh_tokens (token_hash, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (token_hash, user_id, now, now + JWT_REFRESH_TTL_SECONDS),
        )
        conn.commit()


def create_token_pair(user_id: int, email: str) -> tuple[str, str]:
    access_token = _create_access_token(user_id, email)
    refresh_token = secrets.token_urlsafe(32)
    _store_refresh_token(user_id, refresh_token)
    return access_token, refresh_token


def decode_access_token(token: str) -> int | None:
    if not JWT_SECRET:
        return None
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
    if payload.get("type") != "access":
        return None
    sub = payload.get("sub")
    return int(sub) if sub is not None else None


def verify_refresh_token(raw_token: str) -> int | None:
    token_hash = _hash_refresh_token(raw_token)
    conn = get_conn()
    with get_lock():
        cur = conn.execute(
            "SELECT user_id, expires_at FROM refresh_tokens WHERE token_hash = ?",
            (token_hash,),
        )
        row = cur.fetchone()
    if not row:
        return None
    user_id, expires_at = row
    if expires_at < time.time():
        revoke_refresh_token(raw_token)
        return None
    return user_id


def revoke_refresh_token(raw_token: str) -> None:
    token_hash = _hash_refresh_token(raw_token)
    conn = get_conn()
    with get_lock():
        conn.execute("DELETE FROM refresh_tokens WHERE token_hash = ?", (token_hash,))
        conn.commit()


def rotate_refresh_token(raw_token: str) -> tuple[str, str, str] | None:
    token_hash = _hash_refresh_token(raw_token)
    now = time.time()
    conn = get_conn()
    with get_lock():
        cur = conn.execute(
            "SELECT user_id, expires_at FROM refresh_tokens WHERE token_hash = ?",
            (token_hash,),
        )
        row = cur.fetchone()
        if not row:
            return None
            
        user_id, expires_at = row
        conn.execute("DELETE FROM refresh_tokens WHERE token_hash = ?", (token_hash,))
        
        if expires_at < now:
            conn.commit()
            return None
            
        cur = conn.execute("SELECT email FROM users WHERE id = ?", (user_id,))
        user_row = cur.fetchone()
        if not user_row:
            conn.commit()
            return None
            
        email = user_row[0]
        access_token = _create_access_token(user_id, email)
        new_refresh = secrets.token_urlsafe(32)
        new_hash = _hash_refresh_token(new_refresh)
        
        conn.execute(
            "INSERT INTO refresh_tokens (token_hash, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (new_hash, user_id, now, now + JWT_REFRESH_TTL_SECONDS),
        )
        conn.commit()
        
    return access_token, new_refresh, email


def cleanup_expired() -> int:
    """Süresi dolmuş refresh token'ları ve eski oauth_states kayıtlarını siler."""
    now = time.time()
    conn = get_conn()
    with get_lock():
        cur1 = conn.execute("DELETE FROM refresh_tokens WHERE expires_at < ?", (now,))
        cur2 = conn.execute("DELETE FROM oauth_states WHERE created_at < ?", (now - 600,))
        cur3 = conn.execute(
            "DELETE FROM spotify_connect_tokens WHERE created_at < ?", (now - 600,)
        )
        cur4 = conn.execute("DELETE FROM rate_limits WHERE reset_at < ?", (now,))
        cur5 = conn.execute("DELETE FROM login_attempts WHERE (locked_until IS NOT NULL AND locked_until < ?) OR (locked_until IS NULL AND last_attempt < ?)", (now, now - 86400))
        conn.commit()
        return cur1.rowcount + cur2.rowcount + cur3.rowcount + cur4.rowcount + cur5.rowcount
