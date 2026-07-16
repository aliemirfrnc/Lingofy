import pytest
from unittest.mock import Mock
from datetime import datetime, timezone

from backend.admin.services.models import RuntimeConfiguration
from backend.admin.services.providers import ISystemClock, ObservabilityContext
from backend.admin.services.exceptions import ConfigurationException
from backend.admin.services.runtime_config.dtos import UpdateConfigDto
from backend.admin.services.runtime_config.domain_service import RuntimeConfigDomainService
from backend.admin.services.runtime_config.application_service import RuntimeConfigurationCommandService


class MockClock(ISystemClock):
    def __init__(self):
        self._now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self._now


@pytest.fixture
def mock_clock():
    return MockClock()


def test_domain_create_configuration(mock_clock):
    domain = RuntimeConfigDomainService(mock_clock)
    dto = UpdateConfigDto(settings={"max_users": 100})
    
    config = domain.create_configuration(dto)
    
    assert config.settings == {"max_users": 100}
    assert config.version == 1
    assert config.updated_at == mock_clock.now()


def test_domain_create_configuration_invalid_type(mock_clock):
    domain = RuntimeConfigDomainService(mock_clock)
    
    dto = UpdateConfigDto(settings="not a dict")
    with pytest.raises(ConfigurationException, match="Unsupported configuration settings type"):
        domain.create_configuration(dto)


def test_domain_update_configuration(mock_clock):
    domain = RuntimeConfigDomainService(mock_clock)
    dto = UpdateConfigDto(settings={"max_users": 100})
    config = domain.create_configuration(dto)
    
    update_dto = UpdateConfigDto(settings={"max_users": 200, "maintenance_mode": True})
    updated = domain.update_configuration(config, update_dto)
    
    assert updated.settings == {"max_users": 200, "maintenance_mode": True}
    assert updated.version == 2


def test_command_service_update_configuration_create_new(mock_clock):
    domain = RuntimeConfigDomainService(mock_clock)
    write_repo = Mock()
    event_bus = Mock()
    query_service = Mock()
    # Mock returning an unversioned config (equivalent to not found or initialized)
    query_service.get_configuration.return_value = RuntimeConfiguration(version=0, settings={}, updated_at=mock_clock.now())
    
    cmd_service = RuntimeConfigurationCommandService(domain, write_repo, event_bus, query_service)
    ctx = ObservabilityContext(trace_id="1", correlation_id="2", request_id="3")
    
    config = cmd_service.update_configuration({"threshold": 50}, ctx)
    assert config.settings == {"threshold": 50}
    assert config.version == 1
    
    write_repo.save_configuration.assert_called_once()
    event_bus.publish_sync.assert_called_once_with("RuntimeConfigurationUpdated", {"version": 1, "settings": {"threshold": 50}})


def test_command_service_update_configuration_existing(mock_clock):
    domain = RuntimeConfigDomainService(mock_clock)
    write_repo = Mock()
    event_bus = Mock()
    query_service = Mock()
    
    existing = RuntimeConfiguration(
        version=2, settings={"old_key": 10}, updated_at=mock_clock.now()
    )
    query_service.get_configuration.return_value = existing
    
    cmd_service = RuntimeConfigurationCommandService(domain, write_repo, event_bus, query_service)
    ctx = ObservabilityContext(trace_id="1", correlation_id="2", request_id="3")
    
    config = cmd_service.update_configuration({"old_key": 20}, ctx)
    assert config.settings == {"old_key": 20}
    assert config.version == 3
    
    write_repo.save_configuration.assert_called_once()
    event_bus.publish_sync.assert_called_once()
