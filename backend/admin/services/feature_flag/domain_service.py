"""
Domain Service for Feature Flag.
Pure business logic, no I/O.
"""
from backend.admin.services.models import FeatureFlag
from backend.admin.services.providers import ISystemClock
from backend.admin.services.exceptions import FeatureFlagException
from backend.admin.services.feature_flag.dtos import CreateFeatureFlagDto, UpdateFeatureFlagDto


class FeatureFlagDomainService:
    """Manages feature flag lifecycle and targeting rules validation."""

    VALID_RULE_OPERATORS = {"eq", "in", "contains", "gt", "lt", "percentage"}

    def __init__(self, clock: ISystemClock) -> None:
        self.clock = clock

    def _validate_targeting_rules(self, rules: dict) -> None:
        if not isinstance(rules, dict):
            raise FeatureFlagException("Targeting rules must be a dictionary.")
            
        for key, condition in rules.items():
            if not isinstance(condition, dict) or "op" not in condition or "value" not in condition:
                raise FeatureFlagException(f"Invalid targeting rule for key '{key}'. Must contain 'op' and 'value'.")
            
            if condition["op"] not in self.VALID_RULE_OPERATORS:
                raise FeatureFlagException(f"Invalid operator '{condition['op']}' in targeting rule for key '{key}'.")

            if condition["op"] == "percentage":
                val = condition["value"]
                if not isinstance(val, (int, float)) or not (0 <= val <= 100):
                    raise FeatureFlagException("Percentage value must be a number between 0 and 100.")

    def create_flag(self, dto: CreateFeatureFlagDto) -> FeatureFlag:
        """Create a new feature flag from DTO."""
        if not dto.name:
            raise FeatureFlagException("Feature flag name cannot be empty.")
            
        self._validate_targeting_rules(dto.targeting_rules)
            
        return FeatureFlag(
            name=dto.name,
            is_enabled=dto.is_enabled,
            version=1,
            updated_at=self.clock.now(),
            targeting_rules=dto.targeting_rules
        )

    def update_flag(self, current_flag: FeatureFlag, dto: UpdateFeatureFlagDto) -> FeatureFlag:
        """Update an existing feature flag."""
        if current_flag.name != dto.name:
            raise FeatureFlagException("Cannot change the name of an existing feature flag.")
            
        self._validate_targeting_rules(dto.targeting_rules)
            
        return FeatureFlag(
            name=current_flag.name,
            is_enabled=dto.is_enabled,
            version=current_flag.version + 1,
            updated_at=self.clock.now(),
            targeting_rules=dto.targeting_rules
        )
