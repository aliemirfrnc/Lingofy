# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-25
### Added
- **Production AI Pipeline:** Integrated Groq (Llama-3.3-70b-versatile) for real-time translation with lightning-fast latency.
- **Deep Translator Fallback:** Automated fallback mechanism handling Groq rate limits gracefully.
- **24h TTL LRU Cache:** Server-side caching for translations, reducing API cost effectively to zero for repeated songs.
- **Frontend Queueing:** Prefetch queue with Max Concurrency of 3 and AbortController to cancel redundant requests during rapid song skips.
- **WCAG AA Compliance:** Dynamic background luminance calculation to guarantee contrast for lyrics overlay (up to 85% opacity mask).
- **Glass Panel Translation UI:** Beautiful high-contrast translation boxes that remain 100% visible regardless of album cover brightness.

## [0.8.0] - 2026-05-15
### Added
- **Pronunciation Coach Engine:** Audio recording functionality parsing WebM/Ogg to Whisper API.
- **Phoneme Scoring:** Advanced algorithm matching transcripts to expected text and scoring accuracy, fluency, rhythm, and stress.
- **Shadowing Mode:** Full-screen karaoke layout for intensive speaking practice.

### Changed
- Migrated Auth system to strict HttpOnly Cookies (JWT) replacing unsafe localStorage implementation.

## [0.5.0] - 2026-04-10
### Added
- **Dictionary & Morphology API:** Clickable lyric words fetching instant AI definitions, POS tags, and CEFR levels.
- **Progress Dashboard:** Visual streak counters and vocabulary retention statistics (Spaced Repetition).
- **SQLite Migrations:** Added `auto_migrate_table` script allowing zero-downtime schema evolution.

## [0.1.0] - 2026-01-01
### Added
- Initial release.
- Spotify OAuth Integration.
- Basic synced lyrics rendering.
- Next.js and FastAPI boilerplate.
