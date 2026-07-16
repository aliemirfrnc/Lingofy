import sqlite3
import time
from typing import List, Dict, Any, Optional
from .interfaces import IMetricsWriteRepository

class MetricsWriteRepository(IMetricsWriteRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def insert_operation_metric(self, metric_name: str, value: float, tags_json: Optional[str] = None) -> int:
        cursor = self.conn.execute(
            "INSERT INTO operations_metrics (metric_name, value, tags_json, timestamp) VALUES (?, ?, ?, ?)",
            (metric_name, value, tags_json, time.time())
        )
        return cursor.lastrowid

    def batch_insert_operation_metrics(self, metrics: List[Dict[str, Any]]) -> int:
        query = "INSERT INTO operations_metrics (metric_name, value, tags_json, timestamp) VALUES (?, ?, ?, ?)"
        data = [
            (m["metric_name"], m["value"], m.get("tags_json"), m.get("timestamp", time.time()))
            for m in metrics
        ]
        self.conn.executemany(query, data)
        return len(data)

    def update_provider_metric(self, provider_name: str, model_name: Optional[str], request_count: int, error_count: int, latency: float) -> None:
        self.conn.execute(
            """
            INSERT INTO provider_metrics (provider_name, model_name, request_count, error_count, avg_latency, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (provider_name, model_name, request_count, error_count, latency, time.time())
        )
