import sqlite3
import time
from typing import List, Dict, Any, Optional
from .interfaces import IHealthRepository

class HealthRepository(IHealthRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_health_snapshots(self, limit: int = 50, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM health_snapshots"
        params = []
        if cursor is not None:
            query += " WHERE id < ?"
            params.append(cursor)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        self.conn.row_factory = sqlite3.Row
        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def insert_health_snapshot(self, service_name: str, status: str, details_json: Optional[str]) -> int:
        cursor = self.conn.execute(
            "INSERT INTO health_snapshots (service_name, status, details_json, timestamp) VALUES (?, ?, ?, ?)",
            (service_name, status, details_json, time.time())
        )
        return cursor.lastrowid
