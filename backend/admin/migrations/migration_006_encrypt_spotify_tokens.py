import sqlite3

from backend.core.token_encryption import spotify_token_cipher

def upgrade(conn: sqlite3.Connection):
    rows = conn.execute("SELECT user_id, access_token, refresh_token FROM spotify_accounts").fetchall()
    for user_id, access_token, refresh_token in rows:
        access_plaintext, access_legacy = spotify_token_cipher.decrypt(access_token)
        refresh_plaintext, refresh_legacy = spotify_token_cipher.decrypt(refresh_token)
        if access_legacy or refresh_legacy:
            conn.execute("UPDATE spotify_accounts SET access_token = ?, refresh_token = ? WHERE user_id = ?", (spotify_token_cipher.encrypt(access_plaintext), spotify_token_cipher.encrypt(refresh_plaintext), user_id))

def downgrade(conn: sqlite3.Connection):
    raise RuntimeError("Encrypted OAuth credentials must never be downgraded to plaintext")
