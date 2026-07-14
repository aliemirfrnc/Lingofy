# Security Overview

Lingofy takes user data and API security extremely seriously. This document outlines the defensive mechanisms implemented in the system.

## 1. Authentication & Session Management
- **JWT (JSON Web Tokens):** Used for stateless authentication.
- **HttpOnly Cookies:** Access and Refresh tokens are stored in `HttpOnly`, `Secure`, and `SameSite=Strict` cookies. This makes them inaccessible to JavaScript, completely mitigating Cross-Site Scripting (XSS) attacks aimed at token theft.
- **Token Expiration:** Access tokens have a short TTL (e.g., 15 minutes), requiring frequent rotation via the Refresh token.

## 2. Password Security
- **Argon2 Hashing:** We use Argon2 (via `passlib` and `argon2-cffi`), the winner of the Password Hashing Competition, to securely hash user passwords. It provides resistance against GPU cracking and side-channel attacks.

## 3. Rate Limiting & Abuse Prevention
- **IP-Based Rate Limiting:** Global rate limiting is enforced on all endpoints to prevent DDoS and brute-force attacks.
- **Subscription Limits:** Premium features (like AI Translation and Pronunciation) are strictly limited per user.
- **Race Condition Protection:** The decrement of a user's usage limit is wrapped in a thread-safe `RLock` combined with an atomic Try-Revert block. This ensures that a malicious user cannot bypass daily limits by sending 100 concurrent requests.

## 4. Input Validation & Injection
- **SQL Injection:** All database queries are executed using parameterized queries (`?` in `sqlite3`), eliminating the risk of SQL injection.
- **XSS / CSRF:** React naturally escapes variables preventing XSS. CSRF tokens are not strictly required due to the `SameSite=Strict` cookie policy, but CORS is tightly configured to only allow the production origin.

## 5. Secrets Management
- No secrets (API keys, JWT secrets) are hardcoded in the repository.
- All secrets are injected via the `.env` file.
- The `.env` file is included in `.gitignore` to prevent accidental commits.

## 6. Risk Analysis & Mitigation
- **SQLite Concurrency:** SQLite is currently used in `WAL` mode to handle concurrent reads/writes safely. However, for true horizontal scaling and to eliminate file-locking risks entirely, a migration to PostgreSQL is scheduled.
- **Cache Poisoning:** The AI cache validates JSON responses before saving them to prevent malformed data from breaking the frontend.
