"""Compatibility adapter for the single process-local core event bus.

The former independent queue was never started by application lifecycle code. Keeping
this adapter preserves existing imports while making all publishers and subscribers use
the durable-in-request core contract.
"""
from backend.core.events import EventBus

class CoreEventBusAdapter:
    async def publish(self, event_name: str, payload: dict):
        await EventBus.publish(event_name, payload)

    def publish_sync(self, event_type: str, payload: dict = None) -> None:
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(EventBus.publish(event_type, payload))
        except RuntimeError:
            asyncio.run(EventBus.publish(event_type, payload))

    def subscribe(self, event_name: str, handler):
        EventBus.subscribe(event_name, handler)

    def start(self):
        return None

memory_event_bus = CoreEventBusAdapter()
