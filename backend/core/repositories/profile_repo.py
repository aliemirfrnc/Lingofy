"""
ProfileRepo — data access layer for /api/me endpoints.

Responsibilities:
  - Read / update user core fields (display_name)
  - Read / upsert user_preferences
  - Read / revoke refresh_token sessions
  - No business logic; no SQL validation; pure data access
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.core.db import get_conn, get_lock
from backend.core.logger import get_logger

logger = get_logger("lingofy.repositories.profile")


class ProfileRepo:
    # ------------------------------------------------------------------
    # User core
    # ------------------------------------------------------------------

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Return the user row or None."""
        conn = get_conn()
        with get_lock():
            cur = conn.execute(
                "SELECT id, email, display_name, role, created_at FROM users WHERE id = ?",
                (user_id,),
            )
            row = cur.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "email": row[1],
            "display_name": row[2],
            "role": row[3],
            "created_at": row[4],
        }

    def update_display_name(self, user_id: int, display_name: str) -> None:
        """Update the user's display name."""
        conn = get_conn()
        with get_lock():
            conn.execute(
                "UPDATE users SET display_name = ? WHERE id = ?",
                (display_name.strip(), user_id),
            )
            conn.commit()

    # ------------------------------------------------------------------
    # Preferences
    # ------------------------------------------------------------------

    def get_preferences(self, user_id: int) -> Dict[str, Any]:
        """Return the user's preferences row; insert defaults if missing."""
        conn = get_conn()
        with get_lock():
            cur = conn.execute(
                """
                SELECT theme, interface_language, target_language,
                       daily_goal_minutes, timezone,
                       email_notifications, push_notifications, marketing_emails
                FROM user_preferences
                WHERE user_id = ?
                """,
                (user_id,),
            )
            row = cur.fetchone()
            if not row:
                # Insert defaults
                import time
                now = time.time()
                conn.execute(
                    """
                    INSERT OR IGNORE INTO user_preferences
                        (user_id, theme, interface_language, target_language,
                         daily_goal_minutes, timezone,
                         email_notifications, push_notifications, marketing_emails,
                         created_at, updated_at)
                    VALUES (?, 'system', 'en', 'en', 15, 'UTC', 1, 0, 0, ?, ?)
                    """,
                    (user_id, now, now),
                )
                conn.commit()
                return {
                    "theme": "system",
                    "interface_language": "en",
                    "target_language": "en",
                    "daily_goal_minutes": 15,
                    "timezone": "UTC",
                    "email_notifications": True,
                    "push_notifications": False,
                    "marketing_emails": False,
                }
        return {
            "theme": row[0],
            "interface_language": row[1],
            "target_language": row[2],
            "daily_goal_minutes": row[3],
            "timezone": row[4],
            "email_notifications": bool(row[5]),
            "push_notifications": bool(row[6]),
            "marketing_emails": bool(row[7]),
        }

    def update_preferences(self, user_id: int, updates: Dict[str, Any]) -> None:
        """Upsert partial preference updates for a user."""
        import time
        allowed = {
            "theme", "interface_language", "target_language",
            "daily_goal_minutes", "timezone",
            "email_notifications", "push_notifications", "marketing_emails",
        }
        fields = {k: v for k, v in updates.items() if k in allowed}
        if not fields:
            return
        now = time.time()
        conn = get_conn()
        with get_lock():
            # Ensure row exists first
            conn.execute(
                """
                INSERT OR IGNORE INTO user_preferences
                    (user_id, theme, interface_language, target_language,
                     daily_goal_minutes, timezone,
                     email_notifications, push_notifications, marketing_emails,
                     created_at, updated_at)
                VALUES (?, 'system', 'en', 'en', 15, 'UTC', 1, 0, 0, ?, ?)
                """,
                (user_id, now, now),
            )
            set_clause = ", ".join(f"{k} = ?" for k in fields)
            values = list(fields.values()) + [now, user_id]
            conn.execute(
                f"UPDATE user_preferences SET {set_clause}, updated_at = ? WHERE user_id = ?",
                values,
            )
            conn.commit()

    # ------------------------------------------------------------------
    # Sessions (refresh tokens)
    # ------------------------------------------------------------------

    def list_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """List all active (non-expired) refresh token sessions for a user."""
        import time
        now = time.time()
        conn = get_conn()
        with get_lock():
            cur = conn.execute(
                """
                SELECT session_id, created_at, expires_at
                FROM refresh_tokens
                WHERE user_id = ? AND expires_at > ?
                ORDER BY created_at DESC
                """,
                (user_id, now),
            )
            rows = cur.fetchall()
        return [
            {
                "session_id": row[0],
                "created_at": datetime.utcfromtimestamp(row[1]).isoformat() + "Z",
                "expires_at": datetime.utcfromtimestamp(row[2]).isoformat() + "Z",
            }
            for row in rows
        ]

    def revoke_session(self, user_id: int, session_id: str) -> bool:
        """Revoke a single session by session_id. Returns True if found and deleted."""
        conn = get_conn()
        with get_lock():
            cur = conn.execute(
                "DELETE FROM refresh_tokens WHERE session_id = ? AND user_id = ?",
                (session_id, user_id),
            )
            conn.commit()
        return (cur.rowcount or 0) > 0

    def revoke_other_sessions(self, user_id: int, current_token_hash: str) -> int:
        """Revoke all sessions except the one identified by current_token_hash. Returns count."""
        conn = get_conn()
        with get_lock():
            cur = conn.execute(
                "DELETE FROM refresh_tokens WHERE user_id = ? AND token_hash != ?",
                (user_id, current_token_hash),
            )
            conn.commit()
        return cur.rowcount or 0
