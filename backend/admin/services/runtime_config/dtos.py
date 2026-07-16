"""
DTOs for Runtime Configuration.
"""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class UpdateConfigDto:
    settings: Dict[str, Any]
