import pytest
from unittest.mock import Mock
from datetime import datetime, timezone

from backend.admin.services.models import FeatureFlag
from backend.admin.services.providers import ISystemClock, ObservabilityContext
from backend.admin.services.exceptions import FeatureFlagException
from backend.admin.services.feature_flag.dtos import CreateFeatureFlagDto, UpdateFeatureFlagDto
from backend.admin.services.feature_flag.domain_service import FeatureFlagDomainService
from backend.admin.services.feature_flag.application_service import FeatureFlagCommandService


class MockClock(ISystemClock):
    def __init__(self):
        self._now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    def now(self) -> datetime:
        return self._now


@pytest.fixture
def mock_clock():
    return MockClock()


def test_domain_create_flag(mock_clock):
    domain = FeatureFlagDomainService(mock_clock)
    dto = CreateFeatureFlagDto(name="new_ui", is_enabled=False, targeting_rules={})
    
    flag = domain.create_flag(dto)
    
    assert flag.name == "new_ui"
    assert flag.is_enabled is False
    assert flag.version == 1
    assert flag.targeting_rules == {}


def test_domain_create_flag_invalid_rules(mock_clock):
    domain = FeatureFlagDomainService(mock_clock)
    
    dto1 = CreateFeatureFlagDto(name="new_ui", is_enabled=False, targeting_rules={"user1": "invalid"})
    with pytest.raises(FeatureFlagException, match="Must contain 'op' and 'value'"):
        domain.create_flag(dto1)
        
    dto2 = CreateFeatureFlagDto(name="new_ui", is_enabled=False, targeting_rules={"user1": {"op": "invalid_op", "value": "1"}})
    with pytest.raises(FeatureFlagException, match="Invalid operator"):
        domain.create_flag(dto2)
        
    dto3 = CreateFeatureFlagDto(name="new_ui", is_enabled=False, targeting_rules={"user1": {"op": "percentage", "value": 150}})
    with pytest.raises(FeatureFlagException, match="Percentage value must be"):
        domain.create_flag(dto3)


def test_domain_update_flag(mock_clock):
    domain = FeatureFlagDomainService(mock_clock)
    dto = CreateFeatureFlagDto(name="new_ui", is_enabled=False, targeting_rules={})
    flag = domain.create_flag(dto)
    
    update_dto = UpdateFeatureFlagDto(name="new_ui", is_enabled=True, targeting_rules={"region": {"op": "eq", "value": "EU"}})
    updated = domain.update_flag(flag, update_dto)
    
    assert updated.is_enabled is True
    assert updated.version == 2
    assert updated.targeting_rules == {"region": {"op": "eq", "value": "EU"}}


def test_domain_update_flag_invalid_name(mock_clock):
    domain = FeatureFlagDomainService(mock_clock)
    dto = CreateFeatureFlagDto(name="new_ui", is_enabled=False, targeting_rules={})
    flag = domain.create_flag(dto)
    
    update_dto = UpdateFeatureFlagDto(name="other_ui", is_enabled=True, targeting_rules={})
    with pytest.raises(FeatureFlagException, match="Cannot change the name"):
        domain.update_flag(flag, update_dto)


def test_command_service_create_and_update(mock_clock):
    domain = FeatureFlagDomainService(mock_clock)
    write_repo = Mock()
    event_bus = Mock()
    query_service = Mock()
    
    cmd_service = FeatureFlagCommandService(domain, write_repo, event_bus, query_service)
    ctx = ObservabilityContext(trace_id="1", correlation_id="2", request_id="3")
    
    flag = cmd_service.create_flag("beta_feature", False, {}, ctx)
    assert flag.name == "beta_feature"
    write_repo.create_feature_flag.assert_called_once()
    event_bus.publish_sync.assert_called_once_with("FeatureFlagCreated", {"name": "beta_feature", "is_enabled": False})
    
    updated = cmd_service.update_flag(flag, True, {}, ctx)
    assert updated.is_enabled is True
    assert updated.version == 2
    write_repo.update_feature_flag.assert_called_once()
    
    # Test enable_flag when flag is mock retrieved
    query_service.get_flag.return_value = updated
    enabled = cmd_service.enable_flag("beta_feature", ctx)
    assert enabled.is_enabled is True
    assert enabled.version == 3
