import sqlite3
import time
from typing import List, Dict, Any, Optional
from .interfaces import INotificationReadRepository

class NotificationReadRepository(INotificationReadRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_pending_notifications(self, limit: int = 50) -> List[Dict[str, Any]]:
        query = "SELECT * FROM notification_queue WHERE status = 'PENDING' AND (scheduled_for IS NULL OR scheduled_for <= ?) ORDER BY id ASC LIMIT ?"
        self.conn.row_factory = sqlite3.Row
        rows = self.conn.execute(query, (time.time(), limit)).fetchall()
        return [dict(row) for row in rows]

    def get_notifications_history(self, limit: int = 50, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM notifications_history"
        params = []
        if cursor is not None:
            query += " WHERE id < ?"
            params.append(cursor)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        self.conn.row_factory = sqlite3.Row
        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
