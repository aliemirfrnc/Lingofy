"""
Data Transfer Objects for the Feature Flag domain.
"""
from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class CreateFeatureFlagDto:
    """DTO for creating a feature flag."""
    name: str
    is_enabled: bool
    targeting_rules: Dict[str, Any]


@dataclass(frozen=True)
class UpdateFeatureFlagDto:
    """DTO for updating a feature flag."""
    name: str
    is_enabled: bool
    targeting_rules: Dict[str, Any]
