import time
from backend.core.db import get_conn, get_lock

MAX_ATTEMPTS = 5
LOCKOUT_TIME = 900  # 15 minutes

def record_failed_attempt(ip_address: str, email: str) -> None:
    conn = get_conn()
    now = time.time()
    with get_lock():
        cur = conn.execute("SELECT attempts, locked_until FROM login_attempts WHERE ip_address = ? AND email = ?", (ip_address, email))
        row = cur.fetchone()
        if not row:
            conn.execute("INSERT INTO login_attempts (ip_address, email, attempts, last_attempt) VALUES (?, ?, 1, ?)", (ip_address, email, now))
        else:
            attempts = row[0] + 1
            locked_until = (now + LOCKOUT_TIME) if attempts >= MAX_ATTEMPTS else None
            conn.execute("UPDATE login_attempts SET attempts = ?, last_attempt = ?, locked_until = ? WHERE ip_address = ? AND email = ?",
                         (attempts, now, locked_until, ip_address, email))
        conn.commit()

def reset_attempts(ip_address: str, email: str) -> None:
    conn = get_conn()
    with get_lock():
        conn.execute("DELETE FROM login_attempts WHERE ip_address = ? AND email = ?", (ip_address, email))
        conn.commit()

def is_locked_out(ip_address: str, email: str) -> bool:
    conn = get_conn()
    now = time.time()
    with get_lock():
        cur = conn.execute("SELECT locked_until FROM login_attempts WHERE ip_address = ? AND email = ?", (ip_address, email))
        row = cur.fetchone()
        if row and row[0] and row[0] > now:
            return True
        return False

def logout_all_devices(user_id: int) -> None:
    conn = get_conn()
    with get_lock():
        conn.execute("DELETE FROM refresh_tokens WHERE user_id = ?", (user_id,))
        conn.commit()
