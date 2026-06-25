# Developer Walkthrough

Welcome to the Lingofy codebase! This guide acts as a mental map for new developers trying to understand how data flows through the application.

## 1. Starting Up
When you run `npm run dev` and `uvicorn backend.main:app`, the Next.js app spins up on `localhost:3000` and FastAPI on `localhost:8000`. 
The frontend makes API calls via the wrapper in `frontend/lib/api.js`. This wrapper handles appending credentials (HttpOnly cookies) and catching `401 Unauthorized` errors to trigger silent `/auth/refresh` calls.

## 2. Authentication Flow
- **Code:** `backend/routes/auth.py` & `frontend/components/Auth.jsx`
- When a user logs in, FastAPI generates an `access_token` and `refresh_token`.
- Instead of returning them in JSON, FastAPI calls `response.set_cookie()`.
- The frontend receives the cookies. It never stores the token in memory or localStorage.
- The `api.js` wrapper simply sets `credentials: 'include'` on all `fetch` requests.

## 3. Connecting Spotify
- **Code:** `backend/routes/spotify.py`
- The user clicks "Connect Spotify". The frontend requests an OAuth URL from the backend.
- The user authenticates with Spotify and is redirected to `localhost:3000/callback`.
- The frontend sends the OAuth code to the backend. The backend stores the `access_token` and `refresh_token` in `spotify_accounts` table.

## 4. Fetching Lyrics
- **Code:** `frontend/components/LyricsPlayer.jsx` & `backend/routes/lyrics.py`
- When a song plays, the frontend polls `/spotify/current-track`.
- It extracts the Track Name and Artist, then calls `/lyrics?track=...&artist=...`.
- `LyricsPlayer.jsx` manages an `activeLineIndex` based on the Spotify playback progress in milliseconds.

## 5. The Translation Pipeline (The Hard Part)
- **Code:** `backend/routes/translate.py` & `frontend/components/LyricsPlayer.jsx`
- As the song plays, `LyricsPlayer.jsx` uses an **AbortController** and a **Concurrency Queue (Max 3)**.
- It prefetches the current line, plus 5 lines ahead and 5 lines behind.
- Requests hit `/translate-line`.
- The backend checks the `TTLLRUCache`. If missed, it calls `GroqProvider` (Llama 3).
- If Groq fails (Rate limit 429), the `try/except` block silently catches it and uses `DeepTranslator` (Google Translate).
- The translation is returned and displayed in a high-contrast Glass Panel (`#E8E8E8` text).

## 6. Word Analysis (Dictionary)
- **Code:** `frontend/components/WordPanel.jsx` & `backend/routes/word_info.py`
- User clicks a specific word in the lyrics.
- The frontend sends the word and the entire sentence context to `/api/word-info`.
- The backend uses OpenRouter (e.g., Gemini Flash) with a strict JSON schema prompt.
- The AI returns POS tags, definitions, and CEFR level. This word is saved to the `user_words` table for Spaced Repetition.

## 7. Pronunciation Coach
- **Code:** `frontend/components/PronunciationCoach.jsx` & `backend/routes/pronunciation.py`
- The user records audio using the MediaRecorder API in the browser.
- A `WebM` blob is sent as `FormData` to `/api/pronunciation/analyze`.
- The backend sends the audio to Whisper AI for transcription.
- The backend compares Whisper's transcript to the original lyric line and evaluates phonemes.
- The UI renders the score and highlights specific words the user mispronounced.

## Summary
To fix bugs or add features, locate the corresponding flow above. 
- For UI/State issues, check `components/`.
- For Data/API issues, check `routes/`.
- For AI/Logic issues, check `core/providers/`.
