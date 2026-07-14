import pytest
import asyncio
from backend.core.events import EventBus

@pytest.fixture(autouse=True)
def cleanup_event_bus():
    EventBus.clear()

@pytest.mark.asyncio
async def test_event_bus_sync_handler():
    received = []
    
    def my_handler(payload):
        received.append(payload["msg"])
        
    EventBus.subscribe("test_event", my_handler)
    await EventBus.publish("test_event", {"msg": "hello"})
    
    assert len(received) == 1
    assert received[0] == "hello"

@pytest.mark.asyncio
async def test_event_bus_async_handler():
    received = []
    
    async def my_async_handler(payload):
        received.append(payload["msg"])
        
    EventBus.subscribe("test_event", my_async_handler)
    await EventBus.publish("test_event", {"msg": "world"})
    
    # Wait for the background task to run
    await asyncio.sleep(0.01)
    
    assert len(received) == 1
    assert received[0] == "world"
