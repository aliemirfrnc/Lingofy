import sqlite3
from typing import List, Dict, Any, Optional
from .interfaces import ITelemetryReadRepository

class TelemetryReadRepository(ITelemetryReadRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_telemetry_events(self, limit: int = 50, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM telemetry_events"
        params = []
        if cursor is not None:
            query += " WHERE id < ?"
            params.append(cursor)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        self.conn.row_factory = sqlite3.Row
        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def get_request_logs(self, limit: int = 50, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM request_logs"
        params = []
        if cursor is not None:
            query += " WHERE id < ?"
            params.append(cursor)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        self.conn.row_factory = sqlite3.Row
        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
