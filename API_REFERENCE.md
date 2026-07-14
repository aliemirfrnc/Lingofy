# Lingofy API Reference

## Authentication

All protected routes require an `HttpOnly` cookie containing the JWT `access_token` or a Bearer token in the `Authorization` header.

### 1. `POST /auth/register`
Creates a new user account.
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePassword123"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "status": "ok",
    "email": "user@example.com",
    "message": "Kayıt başarılı."
  }
  ```
  *(Sets `access_token` and `refresh_token` as HttpOnly cookies)*

### 2. `POST /auth/login`
Authenticates a user.
- **Request Body:** Same as Register.
- **Response (200 OK):** Sets cookies.

### 3. `POST /auth/refresh`
Refreshes the access token using a valid refresh token.
- **Request Body:**
  ```json
  {
    "refresh_token": "..."
  }
  ```

---

## Core Features

### 4. `GET /lyrics`
Fetches synchronized lyrics for a given track.
- **Query Parameters:**
  - `track` (string): Track name
  - `artist` (string): Artist name (optional)
- **Response (200 OK):**
  ```json
  {
    "lyrics": ["Line 1", "Line 2"],
    "synced": [
      {"time": 12.5, "text": "Line 1"},
      {"time": 16.0, "text": "Line 2"}
    ]
  }
  ```

### 5. `POST /ai/dictionary`
Provides contextual definition for a word based on the lyrics line.
- **Request Body:**
  ```json
  {
    "word": "hell",
    "context_line": "I don't know where the hell I belong"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "word": "hell",
    "translation": "cehennem (mecazi: kahretsin)",
    "contextual_meaning": "Durumun zorluğunu vurgular.",
    "examples": ["Where the hell are we?"]
  }
  ```

### 6. `POST /ai/pronunciation/evaluate`
Evaluates user's recorded audio against an expected text.
- **Form Data:**
  - `audio` (File): Audio blob (wav/webm)
  - `expected_text` (String): The text the user tried to read.
- **Response (200 OK):**
  ```json
  {
    "overall_score": 85.5,
    "accuracy": 90.0,
    "fluency": 81.0,
    "phonemes": [...]
  }
  ```

### 7. `GET /subscriptions/status`
Returns the user's active plan and daily usage limits.
- **Response (200 OK):**
  ```json
  {
    "plan": {
        "name": "FREE",
        "words_limit": 20
    },
    "usage": {
        "words": 5
    }
  }
  ```

## HTTP Status Codes
- `200 OK`: Request successful.
- `400 Bad Request`: Invalid input parameters.
- `401 Unauthorized`: Missing or invalid authentication token.
- `403 Forbidden`: Subscription limit exceeded (Rate Limiting).
- `429 Too Many Requests`: Global IP rate limit exceeded.
- `500 Internal Server Error`: Backend or AI Provider failure.
