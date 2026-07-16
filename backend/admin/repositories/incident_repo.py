import sqlite3
import time
from typing import List, Dict, Any, Optional
from .interfaces import IIncidentRepository

class IncidentRepository(IIncidentRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_incidents(self, limit: int = 50, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM incident_reports"
        params = []
        if cursor is not None:
            query += " WHERE id < ?"
            params.append(cursor)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        self.conn.row_factory = sqlite3.Row
        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def insert_incident(self, title: str, description: str, severity: str) -> int:
        cursor = self.conn.execute(
            "INSERT INTO incident_reports (title, description, severity, status, created_at) VALUES (?, ?, ?, 'OPEN', ?)",
            (title, description, severity, time.time())
        )
        return cursor.lastrowid

    def update_incident_status(self, incident_id: int, status: str) -> None:
        self.conn.execute(
            "UPDATE incident_reports SET status = ?, resolved_at = ? WHERE id = ?",
            (status, time.time() if status == 'RESOLVED' else None, incident_id)
        )
