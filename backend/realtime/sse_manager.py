"""
SSE (Server-Sent Events) connection manager for personal user streams.

Architecture:
  Route (events.py)
    ↓
  SSEManager (this file) — manages per-user queues
    ↓
  asyncio.Queue — in-memory event bus per connection
"""
import asyncio
import json
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator, Dict, Optional
from backend.core.logger import get_logger

logger = get_logger("lingofy.realtime.sse")

# ---------------------------------------------------------------------------
# DTOs (plain dicts serialised as JSON in the SSE `data:` field)
# ---------------------------------------------------------------------------

def build_notification_event(
    title: str,
    message: str,
    level: str = "info",          # info | success | warning | error
    action_url: Optional[str] = None,
) -> dict:
    """Build a `notification` SSE event payload."""
    return {
        "event": "notification",
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": {
            "title": title,
            "message": message,
            "level": level,
            "action_url": action_url,
        },
    }


def build_job_progress_event(
    job_id: str,
    progress: int,           # 0–100
    label: Optional[str] = None,
) -> dict:
    """Build a `job.progress` SSE event payload."""
    return {
        "event": "job.progress",
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": {
            "job_id": job_id,
            "progress": max(0, min(100, progress)),
            "label": label,
        },
    }


def build_job_completed_event(job_id: str, result: Optional[dict] = None) -> dict:
    return {
        "event": "job.completed",
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": {"job_id": job_id, "result": result or {}},
    }


def build_job_failed_event(job_id: str, reason: str) -> dict:
    return {
        "event": "job.failed",
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": {"job_id": job_id, "reason": reason},
    }


def build_ai_stream_event(chunk: str, job_id: Optional[str] = None) -> dict:
    """Build an `ai.stream` SSE event payload for incremental AI text chunks."""
    return {
        "event": "ai.stream",
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": {"chunk": chunk, "job_id": job_id},
    }


def build_subscription_updated_event(plan_name: str, status: str) -> dict:
    return {
        "event": "subscription.updated",
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": {"plan_name": plan_name, "status": status},
    }


def build_profile_updated_event(field: str) -> dict:
    return {
        "event": "profile.updated",
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "data": {"updated_field": field},
    }


# ---------------------------------------------------------------------------
# SSEManager — per-user async queues
# ---------------------------------------------------------------------------

HEARTBEAT_INTERVAL = 20  # seconds
MAX_QUEUE_SIZE = 100       # drop oldest if full


class SSEConnectionManager:
    """
    Manages one asyncio.Queue per connected user.

    A single user may have multiple browser tabs open; each tab gets its own
    queue keyed by a unique connection_id, all stored under the same user_id.

    Thread-safety: all operations run inside the asyncio event loop.
    """

    def __init__(self) -> None:
        # {user_id: {connection_id: asyncio.Queue}}
        self._connections: Dict[int, Dict[str, asyncio.Queue]] = {}

    def connect(self, user_id: int) -> tuple[str, asyncio.Queue]:
        """Register a new SSE connection for user_id. Returns (connection_id, queue)."""
        connection_id = str(uuid.uuid4())
        queue: asyncio.Queue = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)
        self._connections.setdefault(user_id, {})[connection_id] = queue
        logger.info(f"SSE CONNECT user_id={user_id} conn={connection_id}")
        return connection_id, queue

    def disconnect(self, user_id: int, connection_id: str) -> None:
        """Remove a connection when the client disconnects."""
        user_conns = self._connections.get(user_id, {})
        user_conns.pop(connection_id, None)
        if not user_conns:
            self._connections.pop(user_id, None)
        logger.info(f"SSE DISCONNECT user_id={user_id} conn={connection_id}")

    async def publish(self, user_id: int, event: dict) -> None:
        """
        Publish an event to all active connections for a user.
        If a queue is full, the oldest item is discarded (non-blocking).
        """
        user_conns = self._connections.get(user_id, {})
        if not user_conns:
            return
        raw = json.dumps(event, ensure_ascii=False)
        for conn_id, queue in list(user_conns.items()):
            if queue.full():
                try:
                    queue.get_nowait()  # discard oldest
                except asyncio.QueueEmpty:
                    pass
            await queue.put(raw)

    async def broadcast(self, event: dict) -> None:
        """Publish to every connected user (e.g. system-wide announcements)."""
        for user_id in list(self._connections.keys()):
            await self.publish(user_id, event)

    def active_users(self) -> int:
        return len(self._connections)

    def active_connections(self) -> int:
        return sum(len(conns) for conns in self._connections.values())


# Singleton — imported by routes
sse_manager = SSEConnectionManager()


# ---------------------------------------------------------------------------
# SSE stream generator
# ---------------------------------------------------------------------------

async def event_stream_generator(
    user_id: int,
    queue: asyncio.Queue,
    connection_id: str,
) -> AsyncGenerator[str, None]:
    """
    Async generator consumed by FastAPI's StreamingResponse.

    Yields SSE-formatted text chunks:
      event: <type>
      id: <uuid>
      data: <json>
      (blank line)

    A heartbeat comment (`: ping`) is sent every HEARTBEAT_INTERVAL seconds
    to keep the connection alive through proxies.
    """
    try:
        while True:
            try:
                raw = await asyncio.wait_for(queue.get(), timeout=HEARTBEAT_INTERVAL)
                payload: dict = json.loads(raw)
                event_type = payload.get("event", "message")
                event_id = payload.get("id", str(uuid.uuid4()))
                data = json.dumps(payload.get("data", {}), ensure_ascii=False)
                yield f"event: {event_type}\nid: {event_id}\ndata: {data}\n\n"
            except asyncio.TimeoutError:
                # Heartbeat — keeps TCP alive; clients must ignore `: ping`
                yield ": ping\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        sse_manager.disconnect(user_id, connection_id)
