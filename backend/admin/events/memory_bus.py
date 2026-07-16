import asyncio
import logging
import inspect
from typing import Callable, Dict, List, Any, Optional
from .interfaces import IEventBus

logger = logging.getLogger(__name__)

class MemoryEventBus(IEventBus):
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        if event_type in self._subscribers and handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    def clear(self) -> None:
        self._subscribers.clear()

    async def publish(self, event_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
        if payload is None:
            payload = {}
            
        handlers = self._subscribers.get(event_type, [])
        for handler in handlers:
            try:
                if inspect.iscoroutinefunction(handler):
                    # Fire and forget
                    asyncio.create_task(self._run_async_handler(handler, payload))
                else:
                    handler(payload)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}", exc_info=True)

    def publish_sync(self, event_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.publish(event_type, payload))
        except RuntimeError:
            asyncio.run(self.publish(event_type, payload))

    @staticmethod
    async def _run_async_handler(handler: Callable, payload: Dict[str, Any]):
        try:
            await handler(payload)
        except Exception as e:
            logger.error(f"Background handler error: {e}", exc_info=True)
