import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timezone

from backend.admin.services.models import MetricsSnapshot
from backend.admin.services.providers import ISystemClock, ObservabilityContext
from backend.admin.services.metrics.dtos import MetricsRawData
from backend.admin.services.metrics.domain_service import MetricsDomainService
from backend.admin.services.metrics.application_service import MetricsQueryService, MetricsCommandService


class MockClock(ISystemClock):
    def __init__(self, now_time: datetime):
        self._now = now_time

    def now(self) -> datetime:
        return self._now


@pytest.fixture
def mock_clock():
    return MockClock(datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc))


@pytest.fixture
def base_raw_data():
    return MetricsRawData(
        daily_active_users=100,
        weekly_active_users=500,
        monthly_active_users=1000,
        total_users=5000,
        premium_users=500,
        new_users_last_month=200,
        churned_users_last_month=50,
        retained_users_last_month=950,
        total_session_duration_sec=36000.0,
        total_sessions=2000,
        total_translations=15000,
        total_pronunciations=5000,
        total_ai_requests=10000,
        total_response_time_ms=2500000.0,
        provider_calls={"openai": 8000, "anthropic": 2000},
        cache_hits=8000,
        cache_misses=2000,
        failures=100,
        total_operations=12000,
        ai_cost_per_request=0.0015,
        previous_snapshot=None
    )


def test_domain_service_calculates_kpis_correctly(mock_clock, base_raw_data):
    domain_service = MetricsDomainService(mock_clock)
    snapshot = domain_service.calculate_snapshot(base_raw_data)

    assert isinstance(snapshot, MetricsSnapshot)
    assert snapshot.dau == 100
    assert snapshot.wau == 500
    assert snapshot.mau == 1000
    assert snapshot.stickiness == 0.1  # 100 / 1000
    assert snapshot.retention_rate == 0.95  # 950 / (950 + 50)
    assert snapshot.premium_conversion_rate == 0.1  # 500 / 5000
    assert snapshot.free_conversion_rate == 0.9  # 4500 / 5000
    assert snapshot.churn_rate == 0.01  # 50 / 5000
    assert snapshot.avg_session_duration_sec == 18.0  # 36000 / 2000
    assert snapshot.avg_translation_count == 3.0  # 15000 / 5000
    assert snapshot.avg_pronunciation_count == 1.0  # 5000 / 5000
    assert snapshot.avg_ai_requests == 2.0  # 10000 / 5000
    assert snapshot.avg_response_time_ms == 250.0  # 2500000 / 10000
    assert snapshot.cache_hit_rate == 0.8  # 8000 / 10000
    assert snapshot.failure_rate == (100 / 12000)
    assert snapshot.estimated_ai_cost == 15.0  # 10000 * 0.0015
    assert snapshot.trends["dau_growth"] == 0.0
    assert snapshot.trends["mau_growth"] == 0.0


def test_domain_service_calculates_trends(mock_clock, base_raw_data):
    prev_raw_data = MetricsRawData(
        daily_active_users=80,
        weekly_active_users=400,
        monthly_active_users=800,
        total_users=4000,
        premium_users=400,
        new_users_last_month=100,
        churned_users_last_month=20,
        retained_users_last_month=780,
        total_session_duration_sec=20000.0,
        total_sessions=1000,
        total_translations=10000,
        total_pronunciations=3000,
        total_ai_requests=8000,
        total_response_time_ms=2000000.0,
        provider_calls={},
        cache_hits=0,
        cache_misses=0,
        failures=0,
        total_operations=0,
        ai_cost_per_request=0.0015,
        previous_snapshot=None
    )
    
    current_raw = MetricsRawData(**{**base_raw_data.__dict__, "previous_snapshot": prev_raw_data})
    
    domain_service = MetricsDomainService(mock_clock)
    snapshot = domain_service.calculate_snapshot(current_raw)
    
    assert snapshot.trends["dau_growth"] == 0.25  # (100 - 80) / 80
    assert snapshot.trends["mau_growth"] == 0.25  # (1000 - 80) / 80


def test_query_service_fetches_and_delegates(mock_clock, base_raw_data):
    # Mock Repository
    read_repo = Mock()
    read_repo.get_active_users_count.side_effect = [100, 500, 1000]
    read_repo.get_total_users_count.return_value = 5000
    read_repo.get_premium_users_count.return_value = 500
    read_repo.get_new_users_count.return_value = 200
    read_repo.get_churned_users_count.return_value = 50
    read_repo.get_retained_users_count.return_value = 950
    read_repo.get_total_session_duration_sec.return_value = 36000.0
    read_repo.get_total_sessions_count.return_value = 2000
    read_repo.get_total_translations_count.return_value = 15000
    read_repo.get_total_pronunciations_count.return_value = 5000
    read_repo.get_total_ai_requests_count.return_value = 10000
    read_repo.get_total_response_time_ms.return_value = 2500000.0
    read_repo.get_provider_calls_distribution.return_value = {"openai": 8000, "anthropic": 2000}
    read_repo.get_cache_hits.return_value = 8000
    read_repo.get_cache_misses.return_value = 2000
    read_repo.get_total_failures.return_value = 100
    read_repo.get_total_operations.return_value = 12000
    read_repo.get_ai_cost_per_request.return_value = 0.0015

    domain_service = MetricsDomainService(mock_clock)
    query_service = MetricsQueryService(read_repo, domain_service)

    ctx = ObservabilityContext(trace_id="1", correlation_id="2", request_id="3")
    snapshot = query_service.get_latest_snapshot(ctx)

    assert snapshot.dau == 100
    assert snapshot.mau == 1000


def test_command_service_triggers_and_persists():
    query_service = Mock()
    mock_snapshot = Mock(spec=MetricsSnapshot)
    mock_snapshot.dau = 100
    mock_snapshot.mau = 1000
    mock_snapshot.calculated_at = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    query_service.get_latest_snapshot.return_value = mock_snapshot

    write_repo = Mock()
    event_bus = Mock()

    cmd_service = MetricsCommandService(query_service, write_repo, event_bus)
    ctx = ObservabilityContext(trace_id="1", correlation_id="2", request_id="3")
    
    result = cmd_service.trigger_calculation(ctx)
    
    assert result == mock_snapshot
    assert write_repo.insert_operation_metric.call_count == 2
    event_bus.publish_sync.assert_called_once()
    args, kwargs = event_bus.publish_sync.call_args
    assert args[0] == "MetricCalculated"
    assert args[1]["dau"] == 100
    assert args[1]["mau"] == 1000
