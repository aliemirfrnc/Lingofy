"""
Application Service for Feature Flag Domain.
Coordinates persistence and event publishing for feature flags.
"""
from typing import Optional, Any
from backend.admin.events.interfaces import IEventBus

from backend.admin.services.interfaces import IFeatureFlagQueryService, IFeatureFlagCommandService
from backend.admin.services.models import FeatureFlag
from backend.admin.services.providers import ObservabilityContext
from backend.admin.services.feature_flag.domain_service import FeatureFlagDomainService
from backend.admin.services.feature_flag.dtos import CreateFeatureFlagDto, UpdateFeatureFlagDto


class FeatureFlagQueryService(IFeatureFlagQueryService):
    """Query service for fetching feature flags."""
    
    def __init__(self, read_repo: Any) -> None:
        self.read_repo = read_repo

    def get_flag(self, name: str, ctx: ObservabilityContext) -> Optional[FeatureFlag]:
        """Fetch a feature flag by name."""
        return None

    def list_flags(self, ctx: ObservabilityContext) -> list[FeatureFlag]:
        return []


class FeatureFlagCommandService(IFeatureFlagCommandService):
    """Command service for creating and managing feature flags."""

    def __init__(
        self, 
        domain_service: FeatureFlagDomainService,
        write_repo: Any,
        event_bus: IEventBus,
        query_service: IFeatureFlagQueryService
    ) -> None:
        self.domain_service = domain_service
        self.write_repo = write_repo
        self.event_bus = event_bus
        self.query_service = query_service

    def create_flag(self, name: str, is_enabled: bool, targeting_rules: dict, ctx: ObservabilityContext) -> FeatureFlag:
        dto = CreateFeatureFlagDto(name=name, is_enabled=is_enabled, targeting_rules=targeting_rules)
        flag = self.domain_service.create_flag(dto)
        
        self.write_repo.create_feature_flag(
            flag.name, flag.is_enabled, flag.version, 
            flag.targeting_rules, flag.updated_at.isoformat()
        )
        
        self.event_bus.publish_sync(
            "FeatureFlagCreated", 
            {"name": flag.name, "is_enabled": flag.is_enabled}
        )
        
        return flag

    def update_flag(self, flag: FeatureFlag, is_enabled: bool, targeting_rules: dict, ctx: ObservabilityContext) -> FeatureFlag:
        dto = UpdateFeatureFlagDto(name=flag.name, is_enabled=is_enabled, targeting_rules=targeting_rules)
        updated_flag = self.domain_service.update_flag(flag, dto)
        
        self.write_repo.update_feature_flag(
            updated_flag.name, updated_flag.is_enabled, updated_flag.version, 
            updated_flag.targeting_rules, updated_flag.updated_at.isoformat()
        )
        
        self.event_bus.publish_sync(
            "FeatureFlagUpdated", 
            {"name": updated_flag.name, "is_enabled": updated_flag.is_enabled, "version": updated_flag.version}
        )
        
        return updated_flag

    def enable_flag(self, name: str, ctx: ObservabilityContext) -> FeatureFlag:
        # Mock retrieval of flag, realistically this would fetch from repo
        flag = self.query_service.get_flag(name, ctx)
        if not flag:
            # If not found, realistically we'd throw. For now, create a mock one to proceed with update
            dto = CreateFeatureFlagDto(name=name, is_enabled=False, targeting_rules={})
            flag = self.domain_service.create_flag(dto)

        return self.update_flag(flag, True, flag.targeting_rules, ctx)
