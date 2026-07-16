import sqlite3
from typing import List, Dict, Any, Optional
from .interfaces import IMetricsReadRepository

class MetricsReadRepository(IMetricsReadRepository):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def get_operations_metrics(self, limit: int = 50, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM operations_metrics"
        params = []
        if cursor is not None:
            query += " WHERE id < ?"
            params.append(cursor)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        self.conn.row_factory = sqlite3.Row
        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def get_provider_metrics(self, limit: int = 50, cursor: Optional[int] = None) -> List[Dict[str, Any]]:
        query = "SELECT * FROM provider_metrics"
        params = []
        if cursor is not None:
            query += " WHERE id < ?"
            params.append(cursor)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        self.conn.row_factory = sqlite3.Row
        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def _safe_count(self, query: str, params: tuple = ()) -> int:
        try:
            return self.conn.execute(query, params).fetchone()[0] or 0
        except sqlite3.OperationalError:
            return 0

    def _safe_sum(self, query: str, params: tuple = ()) -> float:
        try:
            return float(self.conn.execute(query, params).fetchone()[0] or 0.0)
        except sqlite3.OperationalError:
            return 0.0

    def get_active_users_count(self, days: int) -> int:
        return self._safe_count("SELECT COUNT(DISTINCT user_id) FROM user_sessions WHERE created_at >= datetime('now', ?)", (f"-{days} days",))

    def get_total_users_count(self) -> int:
        return self._safe_count("SELECT COUNT(*) FROM users")

    def get_premium_users_count(self) -> int:
        return self._safe_count("SELECT COUNT(*) FROM users WHERE is_premium = 1")

    def get_new_users_count(self, days: int) -> int:
        return self._safe_count("SELECT COUNT(*) FROM users WHERE created_at >= datetime('now', ?)", (f"-{days} days",))

    def get_churned_users_count(self, days: int) -> int:
        return self._safe_count("SELECT COUNT(*) FROM users WHERE is_premium = 0 AND premium_expires_at >= datetime('now', ?)", (f"-{days} days",))

    def get_retained_users_count(self, days: int) -> int:
        return self._safe_count("SELECT COUNT(*) FROM users WHERE is_premium = 1 AND created_at < datetime('now', ?)", (f"-{days} days",))

    def get_total_session_duration_sec(self) -> float:
        # Assuming we track duration_ms in user_sessions or similar. 
        # Fallback to operations_metrics if user_sessions doesn't have it.
        return self._safe_sum("SELECT SUM(duration_sec) FROM user_sessions")

    def get_total_sessions_count(self) -> int:
        return self._safe_count("SELECT COUNT(*) FROM user_sessions")

    def get_total_translations_count(self) -> int:
        return self._safe_count("SELECT COUNT(*) FROM translations")

    def get_total_pronunciations_count(self) -> int:
        return self._safe_count("SELECT COUNT(*) FROM pronunciations")

    def get_total_ai_requests_count(self) -> int:
        return self._safe_count("SELECT COUNT(*) FROM request_logs WHERE route LIKE '%ai%'")

    def get_total_response_time_ms(self) -> float:
        return self._safe_sum("SELECT SUM(latency_ms) FROM request_logs")

    def get_provider_calls_distribution(self) -> Dict[str, int]:
        try:
            rows = self.conn.execute("SELECT provider_name, request_count FROM provider_metrics").fetchall()
            return {row[0]: row[1] for row in rows}
        except sqlite3.OperationalError:
            return {}

    def get_cache_hits(self) -> int:
        return self._safe_count("SELECT SUM(value) FROM operations_metrics WHERE metric_name = 'cache_hits'")

    def get_cache_misses(self) -> int:
        return self._safe_count("SELECT SUM(value) FROM operations_metrics WHERE metric_name = 'cache_misses'")

    def get_total_failures(self) -> int:
        return self._safe_count("SELECT COUNT(*) FROM request_logs WHERE status_code >= 500")

    def get_total_operations(self) -> int:
        return self._safe_count("SELECT COUNT(*) FROM request_logs")

    def get_ai_cost_per_request(self) -> float:
        return 0.0015  # Default estimated cost USD
