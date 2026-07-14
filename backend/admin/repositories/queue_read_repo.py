from typing import Dict, Any, List, Optional
import sqlite3
from backend.core.db import get_conn

class QueueReadRepository:
    def __init__(self, conn: sqlite3.Connection = None):
        self.conn = conn or get_conn()

    def get_jobs_paginated(self, cursor_id: Optional[int], limit: int = 50, status_filter: str = None) -> List[Dict[str, Any]]:
        query = "SELECT id, job_name, status, priority, retry_count, created_at, scheduled_at, completed_at FROM job_queue"
        params = []
        conditions = []

        if status_filter:
            conditions.append("status = ?")
            params.append(status_filter)

        if cursor_id is not None:
            conditions.append("id < ?")
            params.append(cursor_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.cursor()
        cursor.execute(query, tuple(params))
        
        jobs = []
        for row in cursor.fetchall():
            jobs.append({
                "id": row[0],
                "job_name": row[1],
                "status": row[2],
                "priority": row[3],
                "retry_count": row[4],
                "created_at": row[5],
                "scheduled_at": row[6],
                "completed_at": row[7]
            })
        return jobs
