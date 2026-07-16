"""
Domain Service for Runtime Configuration.
Pure business logic, no I/O.
"""
from typing import Any
from backend.admin.services.models import RuntimeConfiguration
from backend.admin.services.providers import ISystemClock
from backend.admin.services.exceptions import ConfigurationException
from backend.admin.services.runtime_config.dtos import UpdateConfigDto


class RuntimeConfigDomainService:
    """Manages runtime configuration and schema validation."""

    def __init__(self, clock: ISystemClock) -> None:
        self.clock = clock

    def _validate_settings(self, settings: dict) -> None:
        """Validate that the settings are a dictionary of basic types."""
        if not isinstance(settings, dict):
            raise ConfigurationException(f"Unsupported configuration settings type: {type(settings)}")

    def create_configuration(self, dto: UpdateConfigDto) -> RuntimeConfiguration:
        """Create initial configuration."""
        self._validate_settings(dto.settings)
        
        return RuntimeConfiguration(
            version=1,
            settings=dto.settings,
            updated_at=self.clock.now()
        )

    def update_configuration(self, current_config: RuntimeConfiguration, dto: UpdateConfigDto) -> RuntimeConfiguration:
        """Update existing configuration."""
        self._validate_settings(dto.settings)
            
        return RuntimeConfiguration(
            version=current_config.version + 1,
            settings=dto.settings,
            updated_at=self.clock.now()
        )
