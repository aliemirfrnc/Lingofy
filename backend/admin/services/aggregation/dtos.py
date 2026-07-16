"""
DTOs for Aggregation Service.
"""
from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime

@dataclass(frozen=True)
class AggregationResultDto:
    granularity: str
    period_start: datetime
    period_end: datetime
    metrics: Dict[str, float]
