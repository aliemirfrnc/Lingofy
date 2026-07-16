"""
Data Transfer Objects for the Health domain.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class DependencyStatusDto:
    """Raw status of a dependency."""
    name: str
    is_reachable: bool
    latency_ms: float
    error_message: Optional[str]


@dataclass(frozen=True)
class HealthRawData:
    """Raw health data fetched from dependencies."""
    dependencies: List[DependencyStatusDto]
