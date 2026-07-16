import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from backend.admin.services.models import HealthSnapshot, HealthDependency
from backend.admin.services.providers import ISystemClock, ObservabilityContext
from backend.admin.services.health.dtos import HealthRawData, DependencyStatusDto
from backend.admin.services.health.domain_service import HealthDomainService
from backend.admin.services.health.application_service import HealthQueryService


class MockClock(ISystemClock):
    def __init__(self, now_time: datetime):
        self._now = now_time

    def now(self) -> datetime:
        return self._now


@pytest.fixture
def mock_clock():
    return MockClock(datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))


def test_domain_service_evaluates_healthy(mock_clock):
    domain_service = HealthDomainService(mock_clock)
    
    raw = HealthRawData(
        dependencies=[
            DependencyStatusDto(name="Database", is_reachable=True, latency_ms=10.0, error_message=None),
            DependencyStatusDto(name="AI Providers", is_reachable=True, latency_ms=500.0, error_message=None)
        ]
    )
    
    snapshot = domain_service.evaluate_health(raw)
    
    assert snapshot.level == "Healthy"
    assert snapshot.score == 100
    assert len(snapshot.dependencies) == 2
    assert snapshot.dependencies[0].status == "Healthy"


def test_domain_service_evaluates_degraded_and_critical(mock_clock):
    domain_service = HealthDomainService(mock_clock)
    
    # Degraded AI provider (latency > 800) but DB is healthy
    raw = HealthRawData(
        dependencies=[
            DependencyStatusDto(name="Database", is_reachable=True, latency_ms=10.0, error_message=None),
            DependencyStatusDto(name="AI Providers", is_reachable=True, latency_ms=900.0, error_message=None)
        ]
    )
    
    snapshot = domain_service.evaluate_health(raw)
    
    # Database weight is 3, AI Providers weight is 1. 
    # Total weight = 4
    # DB score = 100 * 3 = 300
    # AI score (Degraded) = 70 * 1 = 70
    # Total = 370 / 4 = 92 -> Healthy
    assert snapshot.score == 92
    assert snapshot.level == "Healthy"
    
    # Critical DB
    raw2 = HealthRawData(
        dependencies=[
            DependencyStatusDto(name="Database", is_reachable=False, latency_ms=0.0, error_message="Connection Refused")
        ]
    )
    snapshot2 = domain_service.evaluate_health(raw2)
    assert snapshot2.level == "Critical"
    assert snapshot2.score == 0


def test_query_service_pings_dependencies(mock_clock):
    domain_service = HealthDomainService(mock_clock)
    health_repo = Mock()
    event_bus = Mock()
    
    db_ping = Mock(return_value=True)
    ai_ping = Mock(return_value=True)
    payment_ping = Mock(side_effect=Exception("Timeout"))
    
    query_service = HealthQueryService(
        domain_service=domain_service,
        health_repo=health_repo,
        event_bus=event_bus,
        db_ping_func=db_ping,
        ai_ping_func=ai_ping,
        payment_ping_func=payment_ping
    )
    
    ctx = ObservabilityContext(trace_id="1", correlation_id="2", request_id="3")
    
    with patch('time.perf_counter', side_effect=[0.0, 0.05, 0.0, 0.1, 0.0, 0.01]):
        snapshot = query_service.check_health(ctx)
        
    assert snapshot.dependencies[0].name == "Database"
    assert snapshot.dependencies[0].status == "Healthy"
    assert snapshot.dependencies[2].name == "Payment Gateway"
    assert snapshot.dependencies[2].status == "Critical"
    
    health_repo.insert_health_snapshot.assert_called_once()
    event_bus.publish_sync.assert_called_once()
