# Subscription API — `/api/subscriptions`

**Version:** 1.0  
**Authentication:** Required (except `GET /plans`)  
**Error format:** RFC7807 JSON

---

## Endpoints

### `GET /api/subscriptions/plans`
Returns all available plans. **No authentication required.**

**Response 200**
```json
[
  {
    "name": "FREE",
    "price": 0,
    "currency": "USD",
    "limits": {
      "songs": 5,
      "words": 20,
      "ai_messages": 10,
      "shadowing_minutes": 5,
      "pronunciation": 5
    },
    "features": {
      "pdf_report": false,
      "ai_mentor": false,
      "speaking_simulation": false
    }
  }
]
```

---

### `GET /api/subscriptions/my-plan`
Returns the current active plan and today's usage counters.

**Response 200**
```json
{
  "plan": { "name": "FREE", "songs_limit": 5, ... },
  "usage": { "songs": 2, "words": 5, ... }
}
```

---

### `GET /api/subscriptions/usage`
Returns granular usage data with limits, remaining quota, and daily reset time.

**Response 200**
```json
{
  "songs": {
    "today": 2,
    "current_period": 2,
    "plan_limit": 5,
    "remaining": 3,
    "reset_at": "2026-07-16T00:00:00+00:00"
  },
  "words": { ... },
  "ai_messages": { ... },
  "pronunciation": { ... },
  "shadowing_minutes": { ... }
}
```

`remaining` is `null` for unlimited plans.

---

### `GET /api/subscriptions/billing-overview`
Returns current plan with subscription dates and last payment summary.

**Response 200**
```json
{
  "plan": { "name": "PRO", "price": 9.99, "currency": "USD" },
  "subscription": {
    "status": "ACTIVE",
    "started_at": "2026-07-01T00:00:00Z",
    "expires_at": "2026-08-01T00:00:00Z",
    "provider": "MOCK",
    "cancel_at_period_end": false
  },
  "last_payment": {
    "amount": 9.99,
    "currency": "USD",
    "status": "success",
    "paid_at": "2026-07-01T00:00:00Z"
  }
}
```

`subscription` is `null` for FREE plan users.  
`last_payment` is `null` if no payment has been made.

---

### `GET /api/subscriptions/invoices`
Returns full payment history for the user.

**Response 200**
```json
[
  {
    "id": 1,
    "provider": "MOCK",
    "amount": 9.99,
    "currency": "USD",
    "status": "success",
    "invoice_id": "inv_123",
    "transaction_id": "txn_456",
    "created_at": "2026-07-01T00:00:00Z"
  }
]
```

---

### `GET /api/subscriptions/invoices/{invoice_id}`
Returns a single payment record.

**Path param**: `invoice_id` (integer)

**Response 200** — Same shape as single invoice object above  
**Response 404** — Invoice not found or not owned by user

---

### `GET /api/subscriptions/history`
Returns all historical subscription records for the user.

**Response 200**
```json
[
  {
    "id": 1,
    "plan_name": "PRO",
    "status": "ACTIVE",
    "provider": "MOCK",
    "started_at": "2026-07-01T00:00:00Z",
    "expires_at": "2026-08-01T00:00:00Z",
    "cancel_at_period_end": false,
    "created_at": "2026-07-01T00:00:00Z"
  }
]
```

---

### `POST /api/subscriptions/upgrade`
Upgrade to a paid plan.

**Request body**
```json
{ "plan_name": "PRO", "payment_method_id": "pm_123" }
```

**Development/Test response 200**
```json
{ "status": "ok", "message": "PRO planına başarıyla yükseltildi!" }
```

**Production response 503 — RFC7807**
```json
{
  "type": "https://lingofy.app/errors/billing-provider-unavailable",
  "title": "Billing Provider Unavailable",
  "status": 503,
  "detail": "The payment provider integration is not yet configured for this environment.",
  "instance": "/api/subscriptions",
  "extensions": {
    "maintenance_code": "BILLING_PROVIDER_NOT_AVAILABLE",
    "provider": "PENDING",
    "retry_after": 86400
  }
}
```

Response includes `Retry-After: 86400` header.

---

### `GET /api/subscriptions/payment-methods`
### `POST /api/subscriptions/payment-methods`

Both return RFC7807 503 until a billing provider is integrated. See upgrade endpoint format above.

---

## BLOCKER-004 Resolution Notes

The previous undocumented `503` string on the upgrade endpoint has been replaced with a fully structured **RFC7807 Problem Details** response. Frontend applications must:

1. Detect `status === 503` and `extensions.maintenance_code === "BILLING_PROVIDER_NOT_AVAILABLE"`
2. Display a "Coming Soon" / maintenance UI state
3. Respect the `Retry-After` header when retrying
