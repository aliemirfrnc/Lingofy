from typing import Dict, Any, Optional
import sqlite3
import time
from backend.core.db import get_conn

class QueueWriteRepository:
    def __init__(self, conn: sqlite3.Connection = None):
        self.conn = conn or get_conn()

    def enqueue_job(self, job_name: str, payload_json: str, priority: int = 0, scheduled_at: Optional[float] = None) -> int:
        cursor = self.conn.cursor()
        if scheduled_at is None:
            scheduled_at = time.time()
            
        cursor.execute('''
            INSERT INTO job_queue (job_name, payload_json, status, priority, created_at, scheduled_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (job_name, payload_json, 'QUEUED', priority, time.time(), scheduled_at))
        return cursor.lastrowid

    def update_job_status(self, job_id: int, status: str, error_text: Optional[str] = None) -> bool:
        cursor = self.conn.cursor()
        completed_at = time.time() if status in ('SUCCESS', 'FAILED', 'DEAD') else None
        
        if completed_at:
            cursor.execute('''
                UPDATE job_queue 
                SET status = ?, error_text = ?, completed_at = ? 
                WHERE id = ?
            ''', (status, error_text, completed_at, job_id))
        else:
            cursor.execute('''
                UPDATE job_queue 
                SET status = ?, error_text = ? 
                WHERE id = ?
            ''', (status, error_text, job_id))
            
        return cursor.rowcount > 0
