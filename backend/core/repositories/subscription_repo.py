from typing import Optional, Dict, Any
from backend.core.db import get_conn, get_lock

class SubscriptionRepo:
    def get_user_plan(self, user_id: int) -> Dict[str, Any]:
        """
        Kullanıcının aktif aboneliğini ve plan limitlerini döner.
        """
        conn = get_conn()
        with get_lock():
            cur = conn.execute("""
                SELECT p.name, p.songs_limit, p.words_limit, p.ai_messages_limit, 
                       p.shadowing_limit, p.pronunciation_limit, p.has_pdf_report, 
                       p.has_ai_mentor, p.has_speaking_sim
                FROM subscriptions s
                JOIN plans p ON s.plan_id = p.id
                WHERE s.user_id = ? AND s.status = 'ACTIVE' AND s.expires_at > strftime('%s', 'now')
                ORDER BY s.expires_at DESC LIMIT 1
            """, (user_id,))
            row = cur.fetchone()
            
            if not row:
                # Fallback to FREE
                cur = conn.execute("SELECT name, songs_limit, words_limit, ai_messages_limit, shadowing_limit, pronunciation_limit, has_pdf_report, has_ai_mentor, has_speaking_sim FROM plans WHERE name = 'FREE'")
                row = cur.fetchone()

            if not row:
                return {"name": "FREE", "songs_limit": 5, "words_limit": 20, "ai_messages_limit": 10, "shadowing_limit": 5, "pronunciation_limit": 5}

            return {
                "name": row[0],
                "songs_limit": row[1],
                "words_limit": row[2],
                "ai_messages_limit": row[3],
                "shadowing_limit": row[4],
                "pronunciation_limit": row[5],
                "has_pdf_report": bool(row[6]),
                "has_ai_mentor": bool(row[7]),
                "has_speaking_sim": bool(row[8])
            }

    def get_usage(self, user_id: int, date_str: str) -> Dict[str, int]:
        conn = get_conn()
        with get_lock():
            cur = conn.execute("SELECT songs_used, word_analysis_used, pronunciation_used, shadowing_minutes, ai_messages FROM usage_limits WHERE user_id = ? AND date_str = ?", (user_id, date_str))
            row = cur.fetchone()
            if not row:
                return {"songs": 0, "words": 0, "pronunciation": 0, "shadowing": 0, "ai_messages": 0}
            return {"songs": row[0], "words": row[1], "pronunciation": row[2], "shadowing": row[3], "ai_messages": row[4]}

    def increment_usage(self, user_id: int, date_str: str, feature: str, amount: int = 1) -> None:
        column_map = {
            "songs": "songs_used",
            "words": "word_analysis_used",
            "pronunciation": "pronunciation_used",
            "shadowing": "shadowing_minutes",
            "ai_messages": "ai_messages"
        }
        col = column_map.get(feature)
        if not col:
            return
            
        conn = get_conn()
        with get_lock():
            conn.execute(f"""
                INSERT INTO usage_limits (user_id, date_str, {col}, created_at)
                VALUES (?, ?, ?, strftime('%s', 'now'))
                ON CONFLICT(user_id, date_str) DO UPDATE SET {col} = {col} + ?
            """, (user_id, date_str, amount, amount))
            conn.commit()
