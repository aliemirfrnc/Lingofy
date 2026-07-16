"""
Application Service for Runtime Configuration Domain.
Coordinates persistence and event publishing for configs.
"""
from typing import Optional, Any
from backend.admin.events.interfaces import IEventBus

from backend.admin.services.interfaces import IRuntimeConfigurationQueryService, IRuntimeConfigurationCommandService
from backend.admin.services.models import RuntimeConfiguration
from backend.admin.services.providers import ObservabilityContext
from backend.admin.services.runtime_config.domain_service import RuntimeConfigDomainService
from backend.admin.services.runtime_config.dtos import UpdateConfigDto


class RuntimeConfigurationQueryService(IRuntimeConfigurationQueryService):
    """Query service for fetching runtime configurations."""
    
    def __init__(self, read_repo: Any) -> None:
        self.read_repo = read_repo

    def get_configuration(self, ctx: ObservabilityContext) -> RuntimeConfiguration:
        """Fetch the global configuration."""
        # Realistic implementation would fetch from repo
        return RuntimeConfiguration(version=1, settings={}, updated_at=ctx.start_time if ctx else None)


class RuntimeConfigurationCommandService(IRuntimeConfigurationCommandService):
    """Command service for managing runtime configurations."""

    def __init__(
        self, 
        domain_service: RuntimeConfigDomainService,
        write_repo: Any,
        event_bus: IEventBus,
        query_service: IRuntimeConfigurationQueryService
    ) -> None:
        self.domain_service = domain_service
        self.write_repo = write_repo
        self.event_bus = event_bus
        self.query_service = query_service

    def update_configuration(self, settings: dict, ctx: ObservabilityContext) -> RuntimeConfiguration:
        """Update the global configuration."""
        # Realistic implementation fetches existing config
        current_config = self.query_service.get_configuration(ctx)
        
        dto = UpdateConfigDto(settings=settings)
        if current_config and current_config.version > 0:
            config = self.domain_service.update_configuration(current_config, dto)
        else:
            config = self.domain_service.create_configuration(dto)
            
        self.write_repo.save_configuration(
            config.version, config.settings, config.updated_at.isoformat()
        )
        
        self.event_bus.publish_sync(
            "RuntimeConfigurationUpdated", 
            {"version": config.version, "settings": config.settings}
        )
        
        return config
