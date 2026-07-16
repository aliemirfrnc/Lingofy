"""
Data Transfer Objects for the Metrics domain.
"""
from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class MetricsRawData:
    """Raw data fetched from repositories, used for KPI calculation."""
    daily_active_users: int
    weekly_active_users: int
    monthly_active_users: int
    total_users: int
    premium_users: int
    new_users_last_month: int
    churned_users_last_month: int
    retained_users_last_month: int
    total_session_duration_sec: float
    total_sessions: int
    total_translations: int
    total_pronunciations: int
    total_ai_requests: int
    total_response_time_ms: float
    provider_calls: Dict[str, int]
    cache_hits: int
    cache_misses: int
    failures: int
    total_operations: int
    ai_cost_per_request: float
    previous_snapshot: 'MetricsRawData' = None
