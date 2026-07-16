import pytest
import asyncio
from backend.admin.events.memory_bus import MemoryEventBus
from backend.admin.events.constants import USER_LOGIN

@pytest.mark.asyncio
async def test_memory_event_bus_sync_handler():
    bus = MemoryEventBus()
    received = []

    def handler(payload):
        received.append(payload)

    bus.subscribe(USER_LOGIN, handler)
    await bus.publish(USER_LOGIN, {"user_id": 123})

    assert len(received) == 1
    assert received[0]["user_id"] == 123

    bus.unsubscribe(USER_LOGIN, handler)
    await bus.publish(USER_LOGIN, {"user_id": 456})
    
    assert len(received) == 1  # Unchanged

@pytest.mark.asyncio
async def test_memory_event_bus_async_handler():
    bus = MemoryEventBus()
    received = []

    async def handler(payload):
        await asyncio.sleep(0.01)
        received.append(payload)

    bus.subscribe(USER_LOGIN, handler)
    await bus.publish(USER_LOGIN, {"user_id": 789})
    
    # Wait for the async fire-and-forget task to complete
    await asyncio.sleep(0.05)

    assert len(received) == 1
    assert received[0]["user_id"] == 789
