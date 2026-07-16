import sqlite3
import time
from typing import Optional
from .interfaces import IQueueWriteRepository

class QueueWriteRepository(IQueueWriteRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def enqueue_job(self, job_name: str, payload_json: Optional[str] = None, priority: int = 0, scheduled_at: Optional[float] = None) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO job_queue (job_name, payload_json, status, priority, created_at, scheduled_at)
            VALUES (?, ?, 'QUEUED', ?, ?, ?)
            """,
            (job_name, payload_json, priority, time.time(), scheduled_at or time.time())
        )
        return cursor.lastrowid

    def update_job_status(self, job_id: int, status: str, error_text: Optional[str] = None) -> None:
        self.conn.execute(
            "UPDATE job_queue SET status = ?, error_text = ?, completed_at = ? WHERE id = ?",
            (status, error_text, time.time() if status in ['COMPLETED', 'FAILED'] else None, job_id)
        )

    def insert_job_history(self, job_id: int, status: str, error_text: Optional[str] = None) -> int:
        cursor = self.conn.execute(
            "INSERT INTO job_history (job_id, status, error_text, completed_at) VALUES (?, ?, ?, ?)",
            (job_id, status, error_text, time.time())
        )
        return cursor.lastrowid
