# API Documentation

Lingofy exposes a FastAPI-based RESTful API. All protected endpoints require a valid JWT HttpOnly Cookie.

## 1. Authentication Endpoints

### `POST /auth/register`
Creates a new user.
- **Body:** `{ "email": "user@example.com", "password": "securepassword" }`
- **Response:** `200 OK` (Sets `access_token` and `refresh_token` cookies)
- **Errors:** `400 Bad Request` (Email already exists)

### `POST /auth/login`
Authenticates a user.
- **Body:** `{ "email": "user@example.com", "password": "securepassword" }`
- **Response:** `200 OK` (Sets cookies)

### `GET /auth/me`
Returns current user profile.
- **Response:** `{ "id": 1, "email": "user@example.com", "role": "USER" }`

### `POST /auth/refresh`
Refreshes the access token using the refresh token cookie.
- **Response:** `200 OK` (Sets new `access_token` cookie)

---

## 2. Spotify Endpoints

### `GET /spotify/status`
Checks if the user has connected their Spotify account.
- **Response:** `{ "connected": true, "user": "Spotify User Name" }`

### `GET /spotify/current-track`
Fetches the currently playing track.
- **Response:** `{ "is_playing": true, "item": { "name": "Song", "artists": [{"name": "Artist"}], "duration_ms": 200000 }, "progress_ms": 15000 }`

### `PUT /spotify/play` & `PUT /spotify/pause`
Controls playback.
- **Response:** `200 OK`

---

## 3. Lyrics & Translation Endpoints

### `GET /lyrics`
Fetches synced lyrics for a track.
- **Query Params:** `?track=SongName&artist=ArtistName`
- **Response:** 
```json
{
  "lyrics": ["Line 1", "Line 2"],
  "synced": [
    {"time": 12.5, "text": "Line 1"},
    {"time": 18.0, "text": "Line 2"}
  ]
}
```

### `POST /translate-line`
Translates a single lyrics line using Groq AI.
- **Body:** `{ "text": "Hello world", "track_id": "optional_id" }`
- **Response:** `{ "translation": "Merhaba dünya" }`

---

## 4. Learning & Dictionary Endpoints

### `POST /api/word-info`
Fetches a detailed dictionary definition and grammar breakdown.
- **Body:** `{ "word": "running", "context_line": "I am running late." }`
- **Response:**
```json
{
  "word": "running",
  "translation": "koşmak/koşuyor",
  "explanation": "Verb in present participle form.",
  "examples": ["I like running.", "She is running."],
  "level": "A2"
}
```

### `GET /api/progress/stats`
Returns user's learning progress.
- **Response:** `{ "total_words_learned": 150, "accuracy": 85.5, "streak": 5 }`

---

## 5. Pronunciation Endpoints

### `POST /api/pronunciation/analyze`
Analyzes spoken audio against expected text.
- **Content-Type:** `multipart/form-data`
- **Body:** 
  - `audio`: WebM/Ogg Audio File
  - `expected_text`: "Hello world"
- **Response:**
```json
{
  "accuracy": 92.5,
  "fluency": 88.0,
  "overall_score": 90.2,
  "feedback": "Great job! Watch your pronunciation of 'world'."
}
```

---
*See [ARCHITECTURE.md](ARCHITECTURE.md) for Request Lifecycles.*
