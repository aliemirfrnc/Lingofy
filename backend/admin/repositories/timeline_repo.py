import sqlite3
import time
from typing import List, Dict, Any, Optional
from .interfaces import ITimelineRepository

class TimelineRepository(ITimelineRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_user_timeline(self, user_id: int, limit: int = 50, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM user_timeline WHERE user_id = ?"
        params = [user_id]
        if cursor is not None:
            query += " AND id < ?"
            params.append(cursor)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        self.conn.row_factory = sqlite3.Row
        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def insert_user_event(self, user_id: int, event_type: str, metadata_json: Optional[str]) -> int:
        cursor = self.conn.execute(
            "INSERT INTO user_timeline (user_id, event_type, metadata_json, created_at) VALUES (?, ?, ?, ?)",
            (user_id, event_type, metadata_json, time.time())
        )
        return cursor.lastrowid

    def get_audit_events(self, limit: int = 50, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM audit_events"
        params = []
        if cursor is not None:
            query += " WHERE id < ?"
            params.append(cursor)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        self.conn.row_factory = sqlite3.Row
        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def insert_audit_event(self, action: str, admin_id: Optional[int], target_type: Optional[str], target_id: Optional[str], changes_json: Optional[str], ip_address: Optional[str]) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO audit_events (action, admin_id, target_type, target_id, changes_json, ip_address, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (action, admin_id, target_type, target_id, changes_json, ip_address, time.time())
        )
        return cursor.lastrowid
