import sqlite3
import time
from typing import List, Dict, Any, Optional
from .interfaces import ITelemetryWriteRepository

class TelemetryWriteRepository(ITelemetryWriteRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def insert_telemetry_event(self, trace_id: Optional[str], span_id: Optional[str], name: str, attributes_json: Optional[str]) -> int:
        cursor = self.conn.execute(
            "INSERT INTO telemetry_events (trace_id, span_id, name, attributes_json, timestamp) VALUES (?, ?, ?, ?, ?)",
            (trace_id, span_id, name, attributes_json, time.time())
        )
        return cursor.lastrowid

    def batch_insert_telemetry_events(self, events: List[Dict[str, Any]]) -> int:
        query = "INSERT INTO telemetry_events (trace_id, span_id, name, attributes_json, timestamp) VALUES (?, ?, ?, ?, ?)"
        data = [
            (e.get("trace_id"), e.get("span_id"), e["name"], e.get("attributes_json"), e.get("timestamp", time.time()))
            for e in events
        ]
        self.conn.executemany(query, data)
        return len(data)

    def insert_request_log(self, request_id: str, correlation_id: Optional[str], route: str, method: str, status_code: int, latency_ms: float, user_id: Optional[int]) -> int:
        cursor = self.conn.execute(
            """
            INSERT INTO request_logs (request_id, correlation_id, route, method, status_code, latency_ms, user_id, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (request_id, correlation_id, route, method, status_code, latency_ms, user_id, time.time())
        )
        return cursor.lastrowid
