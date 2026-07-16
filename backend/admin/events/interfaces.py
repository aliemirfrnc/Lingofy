from abc import ABC, abstractmethod
from typing import Callable, Any, Dict, Optional

class IEventBus(ABC):
    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable) -> None:
        pass

    @abstractmethod
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    async def publish(self, event_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
        pass

    @abstractmethod
    def publish_sync(self, event_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
        pass
