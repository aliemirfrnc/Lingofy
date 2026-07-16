"""
Application Service for Aggregation Domain.
"""
from typing import Optional, Any
from backend.admin.events.interfaces import IEventBus

from backend.admin.services.interfaces import IAggregationQueryService, IAggregationCommandService
from backend.admin.services.models import AggregationSnapshot
from backend.admin.services.providers import ObservabilityContext
from backend.admin.services.aggregation.domain_service import AggregationDomainService


class AggregationQueryService(IAggregationQueryService):
    """Query service for fetching aggregation snapshots."""
    
    def __init__(self, read_repo: Any) -> None:
        self.read_repo = read_repo

    def get_aggregation(self, granularity: str, ctx: ObservabilityContext) -> AggregationSnapshot:
        """Fetch an aggregation snapshot by granularity."""
        # For realistic implementation, this would fetch from the read repository
        pass


class AggregationCommandService(IAggregationCommandService):
    """Command service for running aggregations."""

    def __init__(
        self, 
        domain_service: AggregationDomainService,
        write_repo: Any,
        event_bus: IEventBus
    ) -> None:
        self.domain_service = domain_service
        self.write_repo = write_repo
        self.event_bus = event_bus

    def run_aggregation(self, granularity: str, ctx: ObservabilityContext) -> AggregationSnapshot:
        """Run a new aggregation."""
        # In a real scenario, raw metrics would be fetched via another service or repo.
        # For now, we mock raw metrics for testing purposes.
        raw_metrics = {"total_users": 1500, "active_sessions": 300}
        
        snapshot = self.domain_service.calculate_aggregation(granularity, raw_metrics)
        
        self.write_repo.save_aggregation(
            snapshot.granularity, 
            snapshot.period_start.isoformat(), 
            snapshot.period_end.isoformat(), 
            snapshot.metrics
        )
        
        self.event_bus.publish_sync(
            "AggregationCompleted", 
            {
                "granularity": snapshot.granularity, 
                "metrics": snapshot.metrics
            }
        )
        
        return snapshot
