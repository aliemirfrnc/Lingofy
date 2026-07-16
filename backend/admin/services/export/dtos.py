"""
DTOs for Export Service.
"""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class RequestExportDto:
    format: str
    params: Dict[str, Any]
