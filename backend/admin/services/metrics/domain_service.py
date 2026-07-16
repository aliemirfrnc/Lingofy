"""
Domain Service for Metrics.
Pure business logic, no I/O.
"""
from typing import Dict

from backend.admin.services.models import MetricsSnapshot
from backend.admin.services.providers import ISystemClock
from backend.admin.services.metrics.dtos import MetricsRawData


class MetricsDomainService:
    """Calculates KPIs and transforms raw data into a Snapshot."""

    def __init__(self, clock: ISystemClock) -> None:
        self.clock = clock

    def calculate_snapshot(self, raw: MetricsRawData) -> MetricsSnapshot:
        """Calculate the full metrics snapshot from raw data."""
        return MetricsSnapshot(
            dau=raw.daily_active_users,
            wau=raw.weekly_active_users,
            mau=raw.monthly_active_users,
            stickiness=self._calc_stickiness(raw.daily_active_users, raw.monthly_active_users),
            retention_rate=self._calc_retention(raw),
            premium_conversion_rate=self._calc_conversion(raw.premium_users, raw.total_users),
            free_conversion_rate=self._calc_free_conversion(raw.total_users, raw.premium_users),
            churn_rate=self._calc_churn(raw.churned_users_last_month, raw.total_users),
            avg_session_duration_sec=self._calc_avg(raw.total_session_duration_sec, raw.total_sessions),
            avg_translation_count=self._calc_avg(raw.total_translations, raw.total_users),
            avg_pronunciation_count=self._calc_avg(raw.total_pronunciations, raw.total_users),
            avg_ai_requests=self._calc_avg(raw.total_ai_requests, raw.total_users),
            avg_response_time_ms=self._calc_avg(raw.total_response_time_ms, raw.total_ai_requests),
            provider_usage=dict(raw.provider_calls),
            cache_hit_rate=self._calc_ratio(raw.cache_hits, raw.cache_hits + raw.cache_misses),
            failure_rate=self._calc_ratio(raw.failures, raw.total_operations),
            estimated_ai_cost=raw.total_ai_requests * raw.ai_cost_per_request,
            trends=self._calc_trends(raw),
            calculated_at=self.clock.now()
        )

    def _calc_stickiness(self, dau: int, mau: int) -> float:
        return (dau / mau) if mau > 0 else 0.0

    def _calc_retention(self, raw: MetricsRawData) -> float:
        total_prev = raw.retained_users_last_month + raw.churned_users_last_month
        return (raw.retained_users_last_month / total_prev) if total_prev > 0 else 0.0

    def _calc_conversion(self, premium: int, total: int) -> float:
        return (premium / total) if total > 0 else 0.0

    def _calc_free_conversion(self, total: int, premium: int) -> float:
        free = total - premium
        return (free / total) if total > 0 else 0.0

    def _calc_churn(self, churned: int, total: int) -> float:
        return (churned / total) if total > 0 else 0.0

    def _calc_avg(self, total_val: float, count: int) -> float:
        return (total_val / count) if count > 0 else 0.0

    def _calc_ratio(self, subset: int, total: int) -> float:
        return (subset / total) if total > 0 else 0.0

    def _calc_trends(self, raw: MetricsRawData) -> Dict[str, float]:
        """Calculate growth trends if previous data exists."""
        if not raw.previous_snapshot:
            return {"dau_growth": 0.0, "mau_growth": 0.0}
        
        prev = raw.previous_snapshot
        return {
            "dau_growth": self._calc_growth(raw.daily_active_users, prev.daily_active_users),
            "mau_growth": self._calc_growth(raw.monthly_active_users, prev.monthly_active_users)
        }

    def _calc_growth(self, current: int, previous: int) -> float:
        if previous == 0:
            return 1.0 if current > 0 else 0.0
        return (current - previous) / previous
