import sqlite3
import time
from typing import Optional
from .interfaces import INotificationWriteRepository

class NotificationWriteRepository(INotificationWriteRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def enqueue_notification(self, type: str, payload_json: str, scheduled_for: Optional[float] = None) -> int:
        cursor = self.conn.execute(
            "INSERT INTO notification_queue (type, payload_json, status, created_at, scheduled_for) VALUES (?, ?, 'PENDING', ?, ?)",
            (type, payload_json, time.time(), scheduled_for)
        )
        return cursor.lastrowid

    def update_notification_status(self, notification_id: int, status: str, error_text: Optional[str] = None) -> None:
        self.conn.execute(
            "UPDATE notification_queue SET status = ?, processed_at = ? WHERE id = ?",
            (status, time.time() if status != 'PENDING' else None, notification_id)
        )

    def insert_history(self, target_type: str, target_id: str, channel: str, title: str, message: str, status: str) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO notifications_history (target_type, target_id, channel, title, message, status, created_at, sent_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (target_type, target_id, channel, title, message, status, time.time(), time.time() if status == 'SENT' else None)
        )
        return cursor.lastrowid
