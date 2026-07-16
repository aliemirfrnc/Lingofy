"""
Domain Service for Aggregation Domain.
"""
from datetime import datetime, timedelta
from typing import Dict, Any

from backend.admin.services.models import AggregationSnapshot
from backend.admin.services.providers import ISystemClock
from backend.admin.services.exceptions import AggregationException
from backend.admin.services.aggregation.dtos import AggregationResultDto


class AggregationDomainService:
    """Manages aggregation business logic."""

    VALID_GRANULARITIES = {"Hourly", "Daily", "Weekly", "Monthly"}

    def __init__(self, clock: ISystemClock) -> None:
        self.clock = clock

    def _validate_granularity(self, granularity: str) -> None:
        if granularity.capitalize() not in self.VALID_GRANULARITIES:
            raise AggregationException(
                f"Unsupported granularity: {granularity}. Must be one of {self.VALID_GRANULARITIES}."
            )

    def calculate_aggregation(self, granularity: str, raw_metrics: Dict[str, float]) -> AggregationSnapshot:
        """Calculate aggregation snapshot from raw metrics."""
        self._validate_granularity(granularity)
        
        now = self.clock.now()
        # Basic period calculation based on granularity
        if granularity.capitalize() == "Hourly":
            period_start = now - timedelta(hours=1)
        elif granularity.capitalize() == "Daily":
            period_start = now - timedelta(days=1)
        elif granularity.capitalize() == "Weekly":
            period_start = now - timedelta(weeks=1)
        else: # Monthly
            period_start = now - timedelta(days=30)
            
        return AggregationSnapshot(
            granularity=granularity.capitalize(),
            period_start=period_start,
            period_end=now,
            metrics=raw_metrics
        )
