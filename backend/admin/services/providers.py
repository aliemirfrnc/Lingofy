"""
Core providers for determinism and observability in Business Services.
"""
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class ObservabilityContext:
    """Context object for tracking and observability."""
    trace_id: str
    correlation_id: str
    request_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    operation: Optional[str] = None
    
    @classmethod
    def generate(cls, id_generator: "IIdGenerator", operation: str = "unknown", user_id: Optional[str] = None) -> "ObservabilityContext":
        """Generate a new observability context."""
        return cls(
            trace_id=id_generator.generate(),
            correlation_id=id_generator.generate(),
            request_id=id_generator.generate(),
            operation=operation,
            user_id=user_id
        )


class ISystemClock(ABC):
    """Interface for system clock to allow deterministic testing."""
    
    @abstractmethod
    def now(self) -> datetime:
        """Get current UTC datetime."""
        pass


class SystemClock(ISystemClock):
    """Concrete implementation of ISystemClock."""
    
    def now(self) -> datetime:
        """Get current UTC datetime."""
        return datetime.now(timezone.utc)


class IIdGenerator(ABC):
    """Interface for ID generation to allow deterministic testing."""
    
    @abstractmethod
    def generate(self) -> str:
        """Generate a unique ID."""
        pass


class UuidGenerator(IIdGenerator):
    """Concrete implementation of IIdGenerator using UUID4."""
    
    def generate(self) -> str:
        """Generate a unique ID."""
        return str(uuid.uuid4())
