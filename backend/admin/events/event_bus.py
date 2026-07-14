from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Awaitable

class EventBus(ABC):
    @abstractmethod
    async def publish(self, event_name: str, payload: Dict[str, Any]):
        """Publish an event to the bus."""
        pass

    @abstractmethod
    def subscribe(self, event_name: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]):
        """Subscribe to an event."""
        pass
