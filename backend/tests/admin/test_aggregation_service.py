import pytest
from unittest.mock import Mock
from datetime import datetime, timezone

from backend.admin.services.providers import ISystemClock, ObservabilityContext
from backend.admin.services.exceptions import AggregationException
from backend.admin.services.aggregation.domain_service import AggregationDomainService
from backend.admin.services.aggregation.application_service import AggregationCommandService


class MockClock(ISystemClock):
    def __init__(self):
        self._now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self._now


@pytest.fixture
def mock_clock():
    return MockClock()


def test_domain_calculate_aggregation_valid(mock_clock):
    domain = AggregationDomainService(mock_clock)
    raw_metrics = {"total_users": 100}
    
    snapshot = domain.calculate_aggregation("Daily", raw_metrics)
    
    assert snapshot.granularity == "Daily"
    assert snapshot.metrics == {"total_users": 100}
    assert snapshot.period_end == mock_clock.now()
    assert (snapshot.period_end - snapshot.period_start).days == 1


def test_domain_calculate_aggregation_invalid_granularity(mock_clock):
    domain = AggregationDomainService(mock_clock)
    
    with pytest.raises(AggregationException, match="Unsupported granularity"):
        domain.calculate_aggregation("Yearly", {})


def test_command_service_run_aggregation(mock_clock):
    domain = AggregationDomainService(mock_clock)
    write_repo = Mock()
    event_bus = Mock()
    
    cmd_service = AggregationCommandService(domain, write_repo, event_bus)
    ctx = ObservabilityContext(trace_id="1", correlation_id="2", request_id="3")
    
    snapshot = cmd_service.run_aggregation("Weekly", ctx)
    
    assert snapshot.granularity == "Weekly"
    assert snapshot.metrics == {"total_users": 1500, "active_sessions": 300}
    
    write_repo.save_aggregation.assert_called_once_with(
        "Weekly", 
        snapshot.period_start.isoformat(), 
        snapshot.period_end.isoformat(), 
        snapshot.metrics
    )
    event_bus.publish_sync.assert_called_once()
    args = event_bus.publish_sync.call_args[0]
    assert args[0] == "AggregationCompleted"
    assert args[1]["granularity"] == "Weekly"
    assert args[1]["metrics"] == snapshot.metrics
