# Security Overview

Lingofy takes data security and API protection seriously. This document outlines the mechanisms used to protect user data, secure authentication, and prevent malicious attacks.

## 1. Authentication (JWT & HttpOnly Cookies)

We **do not** store authentication tokens in `localStorage` or `sessionStorage` to prevent XSS (Cross-Site Scripting) token theft.

- **Access Tokens (15 min):** Short-lived tokens.
- **Refresh Tokens (7 days):** Long-lived tokens stored in the `refresh_tokens` database table.
- **Delivery Mechanism:** Tokens are sent to the client as `HttpOnly`, `Secure`, `SameSite=Lax` cookies. The browser automatically includes them in API requests, meaning JavaScript cannot read them.

## 2. Password Security

- **Hashing:** User passwords are encrypted using `bcrypt` via the `passlib` library before being stored in the SQLite database.
- **Validation:** Passwords must meet complexity requirements on registration.

## 3. Environment Variables & Secrets

Sensitive data is never hardcoded. All keys are loaded via Python's `dotenv`.
Required secrets:
- `JWT_SECRET`: Used to sign the JWT payload.
- `SPOTIFY_CLIENT_SECRET`: Prevents unauthorized OAuth spoofing.
- `GROQ_API_KEY`, `OPENROUTER_API_KEY`: Strictly isolated in backend providers. The frontend NEVER communicates directly with AI providers.

## 4. Rate Limiting & API Abuse Prevention

AI generation is expensive. To protect the API from DDoS and abuse:
- **Global Rate Limiter:** An in-memory/DB hybrid tracks request counts per user IP.
- **Service Limits:** 
  - `POST /translate-line`: Hardcoded daily limits based on subscription tier (e.g., 500 lines/day). Handled by `_check_rate_limit()` in `translate.py`.
  - Concurrency is throttled using `asyncio.Semaphore(3)` to prevent overwhelming upstream AI providers.

## 5. Web Vulnerability Protections

### XSS (Cross-Site Scripting)
- React handles escaping automatically in the frontend.
- Markdown rendering (e.g., dictionary responses) uses strictly sanitized outputs.

### CSRF (Cross-Site Request Forgery)
- FastAPI CORS middleware is strictly configured to only accept requests from allowed origins (`ALLOWED_ORIGINS`).
- SameSite cookies mitigate cross-origin malicious requests.

### SQL Injection
- Lingofy uses parameterized queries in `sqlite3`. 
- String formatting (`f"..."`) is NEVER used for inserting user input into SQL commands. 
*Example:* `cursor.execute("SELECT * FROM users WHERE email=?", (email,))`

## 6. Authorization (RBAC)

- All protected routes depend on `require_user_id` or `require_admin`.
- Endpoint handlers verify user ownership before mutating data (e.g., a user cannot update another user's `pronunciation_goals`).
