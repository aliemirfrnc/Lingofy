import asyncio
import json
import time
from typing import Any, Callable, Dict, List, Awaitable
from backend.admin.events.event_bus import EventBus
from backend.core.logger import get_logger
from backend.core.db import get_conn

logger = get_logger(__name__)

class MemoryEventBus(EventBus):
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Dict[str, Any]], Awaitable[None]]]] = {}
        self._queue = asyncio.Queue()
        self._worker_task = None

    def start(self):
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._worker())

    async def _worker(self):
        logger.info("MemoryEventBus worker started")
        while True:
            try:
                event_name, payload = await self._queue.get()
                
                # Persist to User Timeline if it is a user event
                self._persist_to_timeline(event_name, payload)
                
                # Notify subscribers
                handlers = self._subscribers.get(event_name, [])
                for handler in handlers:
                    try:
                        await handler(payload)
                    except Exception as e:
                        logger.error(f"Error in event handler for {event_name}: {e}")
                
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"EventBus worker error: {e}")

    async def publish(self, event_name: str, payload: Dict[str, Any]):
        await self._queue.put((event_name, payload))

    def subscribe(self, event_name: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]):
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(handler)

    def _persist_to_timeline(self, event_name: str, payload: Dict[str, Any]):
        """
        Automatically pushes recognizable events to the user_timeline table.
        """
        user_id = payload.get("user_id")
        if not user_id:
            return
            
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_timeline (user_id, event_type, metadata_json, created_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, event_name, json.dumps(payload), time.time()))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to persist event {event_name} to timeline: {e}")

# Global instance
memory_event_bus = MemoryEventBus()
