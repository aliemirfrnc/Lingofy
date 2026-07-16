import pytest
from unittest.mock import Mock
from datetime import datetime, timezone

from backend.admin.services.models import QueueJob
from backend.admin.services.providers import ISystemClock, IIdGenerator, ObservabilityContext
from backend.admin.services.exceptions import QueueException
from backend.admin.services.queue.dtos import QueueJobDto
from backend.admin.services.queue.domain_service import QueueDomainService
from backend.admin.services.queue.application_service import QueueCommandService


class MockClock(ISystemClock):
    def __init__(self):
        self._now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self._now


class MockIdGenerator(IIdGenerator):
    def generate(self) -> str:
        return "mock-id-123"


@pytest.fixture
def mock_clock():
    return MockClock()


@pytest.fixture
def mock_id_gen():
    return MockIdGenerator()


def test_domain_create_job(mock_clock, mock_id_gen):
    domain = QueueDomainService(mock_clock, mock_id_gen)
    dto = QueueJobDto(queue_name="emails", payload={"to": "test@test.com"}, priority=5, delay_sec=60)
    
    job = domain.create_job(dto)
    
    assert job.job_id == "mock-id-123"
    assert job.queue_name == "emails"
    assert job.status == "Pending"
    assert job.scheduled_for.timestamp() == (mock_clock.now().timestamp() + 60)


def test_domain_create_job_invalid_priority(mock_clock, mock_id_gen):
    domain = QueueDomainService(mock_clock, mock_id_gen)
    dto = QueueJobDto(queue_name="emails", payload={}, priority=15)
    
    with pytest.raises(QueueException, match="Priority must be"):
        domain.create_job(dto)


def test_domain_transition_to_failed(mock_clock, mock_id_gen):
    domain = QueueDomainService(mock_clock, mock_id_gen)
    dto = QueueJobDto(queue_name="emails", payload={})
    job = domain.create_job(dto)
    
    failed_job = domain.transition_to_failed(job, "Connection timeout")
    
    assert failed_job.status == "Failed"
    assert failed_job.error == "Connection timeout"
    assert failed_job.completed_at == mock_clock.now()


def test_domain_transition_to_retry(mock_clock, mock_id_gen):
    domain = QueueDomainService(mock_clock, mock_id_gen)
    dto = QueueJobDto(queue_name="emails", payload={})
    job = domain.create_job(dto)
    
    # Simulate a failed job
    job = domain.transition_to_failed(job, "Error")
    
    retry_job = domain.transition_to_retry(job, 300)
    
    assert retry_job.status == "Pending"
    assert retry_job.retries == 1
    assert retry_job.scheduled_for.timestamp() == (mock_clock.now().timestamp() + 300)


def test_domain_transition_to_dead_letter(mock_clock, mock_id_gen):
    domain = QueueDomainService(mock_clock, mock_id_gen)
    dto = QueueJobDto(queue_name="emails", payload={})
    job = domain.create_job(dto)
    
    # Manually hack retries to 5 for test
    job = QueueJob(
        job_id=job.job_id, queue_name=job.queue_name, status="Failed",
        priority=job.priority, payload=job.payload, created_at=job.created_at,
        scheduled_for=job.scheduled_for, completed_at=job.completed_at,
        error="Failing forever", retries=5
    )
    
    retry_job = domain.transition_to_retry(job, 300)
    
    assert retry_job.status == "DeadLetter"
    assert retry_job.queue_name == "dead_letter"


def test_command_service_create_job(mock_clock, mock_id_gen):
    domain = QueueDomainService(mock_clock, mock_id_gen)
    write_repo = Mock()
    write_repo.enqueue_job.return_value = 1
    event_bus = Mock()
    
    cmd_service = QueueCommandService(domain, write_repo, event_bus)
    ctx = ObservabilityContext(trace_id="1", correlation_id="2", request_id="3")
    
    job = cmd_service.create_job("emails", {"user": "ali"}, 1, ctx)
    
    assert job.status == "Pending"
    write_repo.enqueue_job.assert_called_once()
    event_bus.publish_sync.assert_called_once_with(
        "JobEnqueued", 
        {"job_id": "mock-id-123", "queue": "emails", "priority": 1}
    )


def test_command_service_cancel_job(mock_clock, mock_id_gen):
    domain = QueueDomainService(mock_clock, mock_id_gen)
    write_repo = Mock()
    event_bus = Mock()
    cmd_service = QueueCommandService(domain, write_repo, event_bus)
    ctx = ObservabilityContext(trace_id="1", correlation_id="2", request_id="3")
    
    dto = QueueJobDto(queue_name="emails", payload={})
    job = domain.create_job(dto)
    
    cancelled_job = cmd_service.cancel_job(job, ctx)
    
    assert cancelled_job.status == "Cancelled"
    write_repo.update_job_status.assert_called_once_with(0, "Cancelled", None)
    event_bus.publish_sync.assert_called_once_with("JobCancelled", {"job_id": "mock-id-123", "queue": "emails"})
