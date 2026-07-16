import pytest
from unittest.mock import Mock
from datetime import datetime, timezone

from backend.admin.services.providers import ISystemClock, ObservabilityContext
from backend.admin.services.exceptions import ExportException
from backend.admin.services.export.dtos import RequestExportDto
from backend.admin.services.export.domain_service import ExportDomainService
from backend.admin.services.export.application_service import ExportCommandService


class MockClock(ISystemClock):
    def __init__(self):
        self._now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self._now


@pytest.fixture
def mock_clock():
    return MockClock()


def test_domain_create_export_job_valid(mock_clock):
    domain = ExportDomainService(mock_clock)
    dto = RequestExportDto(format="csv", params={"days": 30})
    
    job = domain.create_export_job(dto)
    
    assert job.format == "CSV"
    assert job.status == "Pending"
    assert job.requested_at == mock_clock.now()
    assert job.completed_at is None
    assert job.download_url is None
    assert isinstance(job.export_id, str)
    assert len(job.export_id) > 10


def test_domain_create_export_job_invalid_format(mock_clock):
    domain = ExportDomainService(mock_clock)
    dto = RequestExportDto(format="pdf", params={"days": 30})
    
    with pytest.raises(ExportException, match="Unsupported export format"):
        domain.create_export_job(dto)


def test_command_service_request_export(mock_clock):
    domain = ExportDomainService(mock_clock)
    write_repo = Mock()
    event_bus = Mock()
    
    cmd_service = ExportCommandService(domain, write_repo, event_bus)
    ctx = ObservabilityContext(trace_id="1", correlation_id="2", request_id="3")
    
    job = cmd_service.request_export("JSON", {"limit": 100}, ctx)
    
    assert job.format == "JSON"
    assert job.status == "Pending"
    
    write_repo.save_export_job.assert_called_once_with(
        job.export_id, "JSON", "Pending", job.requested_at.isoformat()
    )
    event_bus.publish_sync.assert_called_once()
    args = event_bus.publish_sync.call_args[0]
    assert args[0] == "ExportRequested"
    assert args[1]["format"] == "JSON"
    assert args[1]["params"] == {"limit": 100}
    assert args[1]["export_id"] == job.export_id
