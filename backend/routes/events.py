"""
GET /api/events/stream — Personal SSE stream endpoint.

Authentication: HTTP-only cookie or Bearer header (existing require_user_id).
Rate Limit: applied by global CSRF/rate middleware in main.py.

OpenAPI summary:
  Opens a persistent Server-Sent Events stream for the authenticated user.
  The stream multiplexes the following event types on a single connection:

    notification        — in-app notification messages
    job.progress        — async job progress updates (0–100)
    job.completed       — async job completion
    job.failed          — async job failure
    ai.stream           — incremental AI text chunks
    subscription.updated — subscription plan changes
    profile.updated     — profile field changes

  The server sends a `: ping` heartbeat comment every 20 seconds.
  Clients should reconnect automatically (EventSource does this natively).

Response:
  200 text/event-stream   — live SSE stream
  401 Unauthorized        — missing / invalid session
  429 Too Many Requests   — rate limited
"""
from fastapi import APIRouter, Request, Header
from fastapi.responses import StreamingResponse

from backend.routes.auth import require_user_id
from backend.realtime.sse_manager import sse_manager, event_stream_generator
from backend.core.logger import get_logger

logger = get_logger("lingofy.routes.events")

router = APIRouter(prefix="/api/events", tags=["realtime"])


@router.get(
    "/stream",
    summary="Personal SSE stream",
    response_description=(
        "A persistent text/event-stream delivering notification, job.progress, "
        "job.completed, job.failed, ai.stream, subscription.updated, "
        "profile.updated events."
    ),
)
async def personal_sse_stream(
    request: Request,
    authorization: str | None = Header(default=None),
):
    """
    Opens a personal Server-Sent Events stream for the authenticated user.

    - **Authentication**: HTTP-only session cookie or `Authorization: Bearer <token>`.
    - **Reconnect**: Use the `Last-Event-ID` header (browser EventSource handles this).
    - **Heartbeat**: Server sends `: ping` every 20 s to keep the connection alive.
    - **Multiplexing**: All event types are delivered on this single channel.
    """
    user_id = require_user_id(request, authorization)
    connection_id, queue = sse_manager.connect(user_id)
    logger.info(
        f"SSE stream opened user_id={user_id} conn={connection_id} "
        f"ip={request.client.host if request.client else 'unknown'}"
    )

    generator = event_stream_generator(user_id, queue, connection_id)

    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",        # Disable Nginx buffering
            "Connection": "keep-alive",
            "Access-Control-Allow-Credentials": "true",
        },
    )
