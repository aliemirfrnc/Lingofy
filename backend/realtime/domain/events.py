from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
import uuid

@dataclass(frozen=True)
class EventMetadata:
    trace_id: str
    correlation_id: str
    request_id: Optional[str]
    timestamp: datetime
    version: str = "1.0"

@dataclass(frozen=True)
class DomainEvent:
    id: str
    type: str
    payload: Dict[str, Any]
    metadata: EventMetadata

def create_event(event_type: str, payload: dict, correlation_id: str, trace_id: str) -> DomainEvent:
    return DomainEvent(
        id=str(uuid.uuid4()),
        type=event_type,
        payload=payload,
        metadata=EventMetadata(
            trace_id=trace_id,
            correlation_id=correlation_id,
            request_id=None,
            timestamp=datetime.utcnow()
        )
    )
