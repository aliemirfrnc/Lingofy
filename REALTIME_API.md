# Realtime API — `/api/events/stream`

**Version:** 1.0  
**Protocol:** Server-Sent Events (SSE)  
**Authentication:** HTTP-only cookie or `Authorization: Bearer <token>`  
**Transport:** HTTP/1.1 persistent connection (`text/event-stream`)

---

## Endpoint

### `GET /api/events/stream`

Opens a personal, persistent SSE stream for the authenticated user.

**Response headers**
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no
```

**Status codes**
| Code | Meaning |
|---|---|
| 200 | Stream established |
| 401 | Missing or expired session |
| 429 | Rate limited |

---

## SSE Wire Format

Each event is sent in standard SSE format:

```
event: <type>
id: <uuid>
data: <json>

```

(Blank line terminates each event.)

### Heartbeat
Every 20 seconds the server sends a keep-alive comment:
```
: ping

```

Clients **must not** treat `: ping` as an event. `EventSource` ignores comments automatically.

---

## Event Types

### `notification`
In-app notification message for the user.

```json
{
  "title": "Practice Reminder",
  "message": "You haven't practised today. Keep your streak!",
  "level": "info",
  "action_url": "/platform/dashboard"
}
```

`level`: `info | success | warning | error`  
`action_url`: optional deep-link

---

### `job.progress`
Async job progress update (0–100).

```json
{
  "job_id": "uuid-here",
  "progress": 45,
  "label": "Analysing pronunciation..."
}
```

---

### `job.completed`
Async job finished successfully.

```json
{
  "job_id": "uuid-here",
  "result": {}
}
```

---

### `job.failed`
Async job failed.

```json
{
  "job_id": "uuid-here",
  "reason": "AI provider timeout"
}
```

---

### `ai.stream`
Incremental AI text chunk (streaming text generation).

```json
{
  "chunk": "Hello, here is",
  "job_id": "uuid-here"
}
```

Clients concatenate chunks in order to reconstruct the full response.

---

### `subscription.updated`
User's subscription plan changed.

```json
{
  "plan_name": "PRO",
  "status": "ACTIVE"
}
```

---

### `profile.updated`
A profile field was updated (e.g. after a PATCH /api/me call).

```json
{
  "updated_field": "display_name"
}
```

---

## Reconnect Behaviour

- Browser `EventSource` reconnects automatically after 3 s on any disconnect.
- Use the `Last-Event-ID` header to resume from the last received event ID.
- The server does **not** replay events — missed events during a disconnect are lost.
  (For durable notifications, poll `GET /api/me` or implement a notification inbox in a future sprint.)

---

## Architecture

```
Client (EventSource)
  ↕  HTTP keep-alive
GET /api/events/stream  (events.py)
  ↓
SSEConnectionManager (realtime/sse_manager.py)
  ↓
asyncio.Queue  (per-connection, in-memory)
  ↑
Any service can publish via: await sse_manager.publish(user_id, event_dict)
```

**Connection lifecycle**
1. `GET /api/events/stream` → `require_user_id` → `sse_manager.connect(user_id)` → returns `(connection_id, queue)`
2. `StreamingResponse` wraps the async generator
3. Generator yields events from the queue; sends `: ping` on 20 s timeout
4. On disconnect, generator finalises → `sse_manager.disconnect(user_id, connection_id)`

**Back-pressure**  
Queue size is capped at 100 events. When full, the oldest message is discarded before enqueueing the new one.
