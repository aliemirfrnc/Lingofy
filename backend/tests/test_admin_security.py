import time

from backend.core.auth import _create_access_token
from backend.core.db import get_conn
from backend.routes.spotify import _get_spotify_row, _save_spotify_tokens

def _admin_user():
    email = f"admin-security-{time.time_ns()}@test.com"
    conn = get_conn()
    conn.execute("INSERT INTO users (email, password_hash, role, created_at) VALUES (?, ?, 'SUPER_ADMIN', ?)", (email, "hash", time.time()))
    user_id = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()[0]
    conn.execute("INSERT OR IGNORE INTO admin_user_roles (user_id, role_id) SELECT ?, id FROM admin_roles WHERE name = 'SUPER_ADMIN'", (user_id,))
    conn.commit()
    return user_id, email

def test_admin_v1_uses_core_jwt_contract(client):
    user_id, email = _admin_user()
    token = _create_access_token(user_id, email)
    response = client.get("/api/admin/v1/dashboard/kpis", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_spotify_tokens_are_encrypted_and_legacy_rows_migrate():
    conn = get_conn()
    email = f"spotify-security-{time.time_ns()}@test.com"
    conn.execute("INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)", (email, "hash", time.time()))
    user_id = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()[0]
    _save_spotify_tokens(user_id, "access", "refresh", 3600)
    stored = conn.execute("SELECT access_token, refresh_token FROM spotify_accounts WHERE user_id = ?", (user_id,)).fetchone()
    assert stored[0].startswith("enc:v1:") and stored[1].startswith("enc:v1:")
    assert _get_spotify_row(user_id)[:2] == ("access", "refresh")
    conn.execute("UPDATE spotify_accounts SET access_token = 'legacy-access', refresh_token = 'legacy-refresh' WHERE user_id = ?", (user_id,))
    conn.commit()
    assert _get_spotify_row(user_id)[:2] == ("legacy-access", "legacy-refresh")
    assert conn.execute("SELECT access_token FROM spotify_accounts WHERE user_id = ?", (user_id,)).fetchone()[0].startswith("enc:v1:")
