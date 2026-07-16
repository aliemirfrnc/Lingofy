import pytest
from unittest.mock import Mock
from datetime import datetime, timezone

from backend.admin.services.models import Incident
from backend.admin.services.providers import ISystemClock, IIdGenerator, ObservabilityContext
from backend.admin.services.exceptions import IncidentException
from backend.admin.services.incident.dtos import CreateIncidentDto, UpdateIncidentStatusDto
from backend.admin.services.incident.domain_service import IncidentDomainService
from backend.admin.services.incident.application_service import IncidentCommandService


class MockClock(ISystemClock):
    def __init__(self):
        self._now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self._now


class MockIdGenerator(IIdGenerator):
    def generate(self) -> str:
        return "incident-123"


@pytest.fixture
def mock_clock():
    return MockClock()


@pytest.fixture
def mock_id_gen():
    return MockIdGenerator()


def test_domain_create_incident(mock_clock, mock_id_gen):
    domain = IncidentDomainService(mock_clock, mock_id_gen)
    dto = CreateIncidentDto(title="DB Down", description="No connection", severity="Critical")
    
    incident = domain.create_incident(dto)
    
    assert incident.incident_id == "incident-123"
    assert incident.status == "Open"
    assert incident.severity == "Critical"


def test_domain_create_incident_invalid_severity(mock_clock, mock_id_gen):
    domain = IncidentDomainService(mock_clock, mock_id_gen)
    dto = CreateIncidentDto(title="x", description="y", severity="SuperCritical")
    
    with pytest.raises(IncidentException, match="Invalid severity"):
        domain.create_incident(dto)


def test_domain_transition_status_valid(mock_clock, mock_id_gen):
    domain = IncidentDomainService(mock_clock, mock_id_gen)
    dto = CreateIncidentDto(title="DB Down", description="No connection", severity="High")
    incident = domain.create_incident(dto)
    
    trans_dto = UpdateIncidentStatusDto(incident_id="incident-123", new_status="Investigating")
    updated = domain.transition_status(incident, trans_dto)
    
    assert updated.status == "Investigating"
    
    trans_dto2 = UpdateIncidentStatusDto(incident_id="incident-123", new_status="Resolved", resolution_notes="Restarted")
    resolved = domain.transition_status(updated, trans_dto2)
    
    assert resolved.status == "Resolved"
    assert resolved.resolved_at == mock_clock.now()


def test_domain_transition_status_invalid(mock_clock, mock_id_gen):
    domain = IncidentDomainService(mock_clock, mock_id_gen)
    dto = CreateIncidentDto(title="DB Down", description="No connection", severity="Low")
    incident = domain.create_incident(dto)
    
    # Can't resolve without resolution notes if severity was High, but here it is Low.
    trans_dto = UpdateIncidentStatusDto(incident_id="incident-123", new_status="Resolved")
    resolved = domain.transition_status(incident, trans_dto)
    assert resolved.status == "Resolved"
    
    # Try transitioning from Resolved to Open (invalid)
    with pytest.raises(IncidentException, match="Cannot transition from"):
        domain.transition_status(resolved, UpdateIncidentStatusDto(incident_id="x", new_status="Open"))


def test_command_service_report_incident(mock_clock, mock_id_gen):
    domain = IncidentDomainService(mock_clock, mock_id_gen)
    write_repo = Mock()
    event_bus = Mock()
    slack_provider = Mock()
    email_provider = Mock()
    
    cmd_service = IncidentCommandService(domain, write_repo, event_bus, slack_provider, email_provider)
    ctx = ObservabilityContext(trace_id="1", correlation_id="2", request_id="3")
    
    incident = cmd_service.open_incident("Cache Miss Spikes", "Critical", ctx)
    
    assert incident.status == "Open"
    write_repo.create_incident.assert_called_once()
    slack_provider.send.assert_called_once()
    email_provider.send.assert_called_once()
    event_bus.publish_sync.assert_called_once_with("IncidentCreated", {"incident_id": "incident-123", "severity": "Critical"})


def test_command_service_update_status(mock_clock, mock_id_gen):
    domain = IncidentDomainService(mock_clock, mock_id_gen)
    write_repo = Mock()
    event_bus = Mock()
    slack_provider = Mock()
    email_provider = Mock()
    
    cmd_service = IncidentCommandService(domain, write_repo, event_bus, slack_provider, email_provider)
    ctx = ObservabilityContext(trace_id="1", correlation_id="2", request_id="3")
    
    dto = CreateIncidentDto(title="API Timeout", description="5xx", severity="High")
    incident = domain.create_incident(dto)
    
    updated = cmd_service.update_status(incident, "Resolved", "Deployed fix", ctx)
    
    assert updated.status == "Resolved"
    write_repo.update_incident_status.assert_called_once()
    slack_provider.send.assert_called_once() # Should notify on resolve
    event_bus.publish_sync.assert_called_once_with("IncidentStatusUpdated", {"incident_id": "incident-123", "new_status": "Resolved"})
