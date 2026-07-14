import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class EventBus:
    _subscribers: Dict[str, List[Callable]] = {}

    @classmethod
    def subscribe(cls, event_type: str, handler: Callable):
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = []
        if handler not in cls._subscribers[event_type]:
            cls._subscribers[event_type].append(handler)

    @classmethod
    def clear(cls):
        cls._subscribers.clear()

    @classmethod
    async def publish(cls, event_type: str, payload: dict = None):
        if payload is None:
            payload = {}
        handlers = cls._subscribers.get(event_type, [])
        import inspect
        for handler in handlers:
            try:
                if inspect.iscoroutinefunction(handler):
                    asyncio.create_task(cls._run_async_handler(handler, payload))
                else:
                    handler(payload)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}", exc_info=True)

    @staticmethod
    async def _run_async_handler(handler, payload):
        try:
            await handler(payload)
        except Exception as e:
            logger.error(f"Background handler error: {e}", exc_info=True)
