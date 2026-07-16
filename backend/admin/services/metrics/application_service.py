"""
Application Service for Metrics Domain.
Coordinates CQRS Repositories, delegates to Domain Service, and publishes Domain Events.
"""
from typing import Optional, Any
from backend.admin.events.interfaces import IEventBus

from backend.admin.repositories.interfaces import IMetricsReadRepository, IMetricsWriteRepository
from backend.admin.services.interfaces import IMetricsQueryService, IMetricsCommandService
from backend.admin.services.models import MetricsSnapshot
from backend.admin.services.providers import ObservabilityContext, ISystemClock
from backend.admin.services.metrics.domain_service import MetricsDomainService
from backend.admin.services.metrics.dtos import MetricsRawData


class MetricsQueryService(IMetricsQueryService):
    """Query service for fetching current metrics snapshots."""

    def __init__(self, read_repo: IMetricsReadRepository, domain_service: MetricsDomainService) -> None:
        self.read_repo = read_repo
        self.domain_service = domain_service

    def get_latest_snapshot(self, ctx: ObservabilityContext) -> MetricsSnapshot:
        """Fetch raw data and let Domain Service generate the snapshot."""
        # Note: we assume the read repo has these abstract methods
        raw = MetricsRawData(
            daily_active_users=self.read_repo.get_active_users_count(days=1),
            weekly_active_users=self.read_repo.get_active_users_count(days=7),
            monthly_active_users=self.read_repo.get_active_users_count(days=30),
            total_users=self.read_repo.get_total_users_count(),
            premium_users=self.read_repo.get_premium_users_count(),
            new_users_last_month=self.read_repo.get_new_users_count(days=30),
            churned_users_last_month=self.read_repo.get_churned_users_count(days=30),
            retained_users_last_month=self.read_repo.get_retained_users_count(days=30),
            total_session_duration_sec=self.read_repo.get_total_session_duration_sec(),
            total_sessions=self.read_repo.get_total_sessions_count(),
            total_translations=self.read_repo.get_total_translations_count(),
            total_pronunciations=self.read_repo.get_total_pronunciations_count(),
            total_ai_requests=self.read_repo.get_total_ai_requests_count(),
            total_response_time_ms=self.read_repo.get_total_response_time_ms(),
            provider_calls=self.read_repo.get_provider_calls_distribution(),
            cache_hits=self.read_repo.get_cache_hits(),
            cache_misses=self.read_repo.get_cache_misses(),
            failures=self.read_repo.get_total_failures(),
            total_operations=self.read_repo.get_total_operations(),
            ai_cost_per_request=self.read_repo.get_ai_cost_per_request(),
            previous_snapshot=None  # We could fetch a previous raw data if we tracked it
        )
        return self.domain_service.calculate_snapshot(raw)


class MetricsCommandService(IMetricsCommandService):
    """Command service for triggering metric aggregations and logging them."""

    def __init__(
        self, 
        query_service: IMetricsQueryService, 
        write_repo: IMetricsWriteRepository,
        event_bus: IEventBus
    ) -> None:
        self.query_service = query_service
        self.write_repo = write_repo
        self.event_bus = event_bus

    def trigger_calculation(self, ctx: ObservabilityContext) -> MetricsSnapshot:
        """Trigger a calculation, persist it, and publish an event."""
        # 1. Coordinate calculation
        snapshot = self.query_service.get_latest_snapshot(ctx)
        
        # 2. Persist using Write Repository
        self.write_repo.insert_operation_metric(
            metric_name="dau", value=float(snapshot.dau)
        )
        self.write_repo.insert_operation_metric(
            metric_name="mau", value=float(snapshot.mau)
        )
        
        # 3. Publish domain event
        self.event_bus.publish_sync(
            "MetricCalculated", 
            {"dau": snapshot.dau, "mau": snapshot.mau, "calculated_at": snapshot.calculated_at.isoformat()}
        )
        
        return snapshot
