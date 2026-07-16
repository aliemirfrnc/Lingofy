"""
Data Transfer Objects for the Queue domain.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass(frozen=True)
class QueueJobDto:
    """DTO for creating or updating a queue job."""
    queue_name: str
    payload: Dict[str, Any]
    priority: int = 0
    scheduled_for: Optional[datetime] = None
    delay_sec: Optional[int] = None
