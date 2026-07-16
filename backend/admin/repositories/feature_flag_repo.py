import sqlite3
import time
from typing import List, Dict, Any, Optional
from .interfaces import IFeatureFlagRepository

class FeatureFlagRepository(IFeatureFlagRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_feature_flags(self) -> List[Dict[str, Any]]:
        self.conn.row_factory = sqlite3.Row
        rows = self.conn.execute("SELECT * FROM feature_flags").fetchall()
        return [dict(row) for row in rows]

    def get_feature_flag(self, name: str) -> Optional[bool]:
        self.conn.row_factory = sqlite3.Row
        row = self.conn.execute("SELECT is_enabled FROM feature_flags WHERE name = ?", (name,)).fetchone()
        return bool(row["is_enabled"]) if row else None

    def set_feature_flag(self, name: str, is_enabled: bool, admin_id: Optional[int] = None) -> None:
        self.conn.row_factory = sqlite3.Row
        row = self.conn.execute("SELECT id, is_enabled FROM feature_flags WHERE name = ?", (name,)).fetchone()
        
        now = time.time()
        
        if row:
            flag_id = row["id"]
            prev_state = bool(row["is_enabled"])
            self.conn.execute("UPDATE feature_flags SET is_enabled = ?, updated_at = ? WHERE id = ?", (is_enabled, now, flag_id))
            self.conn.execute(
                "INSERT INTO feature_flag_history (flag_id, previous_state, new_state, changed_by, changed_at) VALUES (?, ?, ?, ?, ?)",
                (flag_id, prev_state, is_enabled, admin_id, now)
            )
        else:
            cursor = self.conn.execute(
                "INSERT INTO feature_flags (name, is_enabled, updated_at) VALUES (?, ?, ?)",
                (name, is_enabled, now)
            )
            flag_id = cursor.lastrowid
            self.conn.execute(
                "INSERT INTO feature_flag_history (flag_id, previous_state, new_state, changed_by, changed_at) VALUES (?, ?, ?, ?, ?)",
                (flag_id, False, is_enabled, admin_id, now)
            )
