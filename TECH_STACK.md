# Tech Stack Analysis

Lingofy uses a modern, high-performance tech stack optimized for fast iteration, real-time AI processing, and scalable deployment.

## 1. Backend

- **Language:** Python 3.10+
- **Framework:** FastAPI (High performance, async, based on Starlette).
- **Validation:** Pydantic (Strict typing and request/response schema validation).
- **Server:** Uvicorn (ASGI server) + Gunicorn (Process manager for production).
- **HTTP Client:** `httpx` (For asynchronous external requests to Spotify and AI providers).

## 2. Frontend

- **Language:** JavaScript / JSX
- **Framework:** Next.js 14 (App Router)
- **UI Library:** React 18
- **Styling:** Tailwind CSS + Vanilla CSS (for complex dynamic gradients and glassmorphism).
- **Audio API:** HTML5 Web Audio API, MediaRecorder API (for capturing WebM microphone input).

## 3. Database & Caching

- **Database:** SQLite3
  - Lightweight, embedded, zero-configuration.
  - Custom idempotent migration scripts (`db.py`).
  - Strict Foreign Key constraints and cascading deletes.
- **Caching:** Custom `TTLLRUCache`
  - In-memory thread-safe dictionary with `asyncio.Lock()`.
  - 24-hour TTL for LLM payloads, saving immense API costs.

## 4. Artificial Intelligence

- **AI Gateways:**
  - **OpenRouter:** Dynamic routing between models (Gemini Flash, GPT-4o-mini).
  - **Groq:** Lightning-fast inference using LPUs (Llama-3.3-70b-versatile).
- **Transcriptions:** Whisper API (Voice to text).
- **Translation Fallback:** `deep_translator` (Google Translate wrapper for catastrophic AI failure).

## 5. Security & Authentication

- **Hashing:** `passlib` with `bcrypt`.
- **Tokens:** `PyJWT` (JSON Web Tokens).
- **Delivery:** FastAPI `Response.set_cookie` (`HttpOnly`, `Secure`, `SameSite=Lax`).
- **OAuth:** Direct integration with Spotify's OAuth 2.0 PKCE flow.

## 6. DevOps & Deployment

- **Containerization:** Docker & Docker Compose.
- **Web Server / Reverse Proxy:** Nginx (Handles SSL termination and proxying to Uvicorn/Next.js).
- **Certificates:** Let's Encrypt (Certbot).
- **Linting & Formatting:** ESLint (Frontend), Black (Backend).
