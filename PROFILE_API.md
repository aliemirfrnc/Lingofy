# Profile API — `/api/me`

**Version:** 1.0  
**Authentication:** HTTP-only cookie or `Authorization: Bearer <token>`  
**Rate limit:** 300 req/min (standard tier)  
**Error format:** RFC7807 JSON

---

## Endpoints

### `GET /api/me`
Returns the full profile of the authenticated user.

**Response 200**
```json
{
  "id": 1,
  "email": "user@example.com",
  "display_name": "Ali",
  "role": "USER",
  "created_at": "2026-07-01T12:00:00Z"
}
```

---

### `PATCH /api/me`
Updates the authenticated user's display name.

**Request body**
```json
{ "display_name": "Ali Emir" }
```

**Validation**
- `display_name`: 1–50 characters, non-empty after trimming.

**Response 200** — Updated profile (same shape as GET /api/me)

---

### `GET /api/me/preferences`
Returns user preferences. Defaults are inserted on first access.

**Response 200**
```json
{
  "theme": "system",
  "interface_language": "en",
  "target_language": "en",
  "daily_goal_minutes": 15,
  "timezone": "UTC",
  "email_notifications": true,
  "push_notifications": false,
  "marketing_emails": false
}
```

---

### `PATCH /api/me/preferences`
Partially updates user preferences. All fields optional.

**Request body (all optional)**
```json
{
  "theme": "dark",
  "interface_language": "tr",
  "target_language": "en",
  "daily_goal_minutes": 30,
  "timezone": "Europe/Istanbul",
  "email_notifications": true,
  "push_notifications": false,
  "marketing_emails": false
}
```

**Validation**
- `theme`: `light | dark | system`
- `interface_language` / `target_language`: ISO 639-1 code from `/api/me/languages`
- `daily_goal_minutes`: 5–240 (integer)
- Boolean fields: strict boolean

**Response 200** — Full updated preferences

---

### `GET /api/me/sessions`
Returns all currently active (non-expired) refresh token sessions.

**Response 200**
```json
[
  {
    "session_id": "uuid-here",
    "created_at": "2026-07-15T10:00:00Z",
    "expires_at": "2026-08-14T10:00:00Z"
  }
]
```

> Note: `session_id` is a stable UUID stored server-side. Token hashes are never exposed.

---

### `DELETE /api/me/sessions/{session_id}`
Revoke a specific session by its `session_id`.

**Path param**: `session_id` (UUID)

**Response 200**
```json
{ "session_id": "uuid-here", "status": "revoked" }
```

**Response 404** — Session not found or already expired

---

### `DELETE /api/me/sessions/others`
Revoke all sessions except the current one.  
Identified via the `refresh_token` cookie of the request.

**Response 200**
```json
{ "revoked": 3, "status": "ok" }
```

---

### `GET /api/me/languages`
Returns the static list of languages supported by the platform. No auth required.

**Response 200**
```json
[
  { "code": "en", "name": "English" },
  { "code": "tr", "name": "Turkish" },
  ...
]
```

---

## Database Schema

### `users` table (additions via `auto_migrate_table`)
| Column | Type | Default |
|---|---|---|
| `display_name` | TEXT | `''` |

### `user_preferences` table (new)
| Column | Type | Default |
|---|---|---|
| `user_id` | INTEGER FK | — |
| `theme` | TEXT | `system` |
| `interface_language` | TEXT | `en` |
| `target_language` | TEXT | `en` |
| `daily_goal_minutes` | INTEGER | `15` |
| `timezone` | TEXT | `UTC` |
| `email_notifications` | BOOLEAN | `1` |
| `push_notifications` | BOOLEAN | `0` |
| `marketing_emails` | BOOLEAN | `0` |
| `created_at` | REAL | — |
| `updated_at` | REAL | — |

### `refresh_tokens` table (additions via `auto_migrate_table`)
| Column | Type | Default |
|---|---|---|
| `session_id` | TEXT | NULL |

> `session_id` is assigned on first access. Existing rows will have NULL until refreshed.
