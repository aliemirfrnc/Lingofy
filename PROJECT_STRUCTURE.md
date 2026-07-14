# Project Structure

Lingofy follows a monorepo-style structure containing both the Next.js frontend and FastAPI backend.

```text
C:\Projeler\SpotifyBenzeri
├── backend/
│   ├── core/                  # Core Business Logic & Configurations
│   │   ├── providers/         # External Integrations (AI Factory, Groq, OpenRouter)
│   │   ├── repositories/      # Data access layer (Future scalability)
│   │   ├── services/          # Business services (Dictionary, Translations)
│   │   ├── auth.py            # JWT and Security logic
│   │   ├── cache_store.py     # TTL LRU Cache Implementation
│   │   ├── config.py          # Environment Variables Parsing
│   │   └── db.py              # SQLite setup and idempotent migrations
│   ├── data/                  # SQLite database files (.db)
│   ├── dependencies/          # FastAPI Dependency Injections
│   ├── prompts/               # AI System Prompts (JSON schemas, Persona rules)
│   ├── routes/                # FastAPI Routers (Controllers)
│   │   ├── auth.py            # Login, Register, Cookies
│   │   ├── chat.py            # AI Chatbot Endpoints
│   │   ├── lyrics.py          # Spotify synced lyrics fetcher
│   │   ├── progress.py        # Dashboard stats
│   │   ├── pronunciation.py   # Audio analysis via Whisper
│   │   ├── spotify.py         # OAuth, Playback control
│   │   ├── subscriptions.py   # Membership plans
│   │   ├── translate.py       # Groq/DeepTranslator logic
│   │   └── word_info.py       # Morphology & Dictionary
│   ├── main.py                # FastAPI Application Entrypoint
│   └── requirements.txt       # Python dependencies
│
├── frontend/
│   ├── components/            # Reusable React UI Components
│   │   ├── ui/                # Base UI elements (Avatar, Card)
│   │   ├── Auth.jsx           # Registration/Login forms
│   │   ├── DynamicBackground.jsx # Color extraction & Luminance rendering
│   │   ├── LyricsPlayer.jsx   # Core scrolling lyrics, Prefetch Queues
│   │   ├── MusicPlayer.jsx    # Spotify Web Playback wrapper
│   │   ├── PronunciationCoach.jsx # Audio recording & feedback UI
│   │   ├── ShadowingMode.jsx  # Full-screen karaoke UI
│   │   └── WordPanel.jsx      # Dictionary slide-over
│   ├── lib/                   # Utilities & API Handlers
│   │   ├── api.js             # Fetch wrappers, Cookie handlers, AbortControllers
│   │   ├── audioRecorder.js   # MediaRecorder API helpers
│   │   └── utils.js           # String formatting, Date parsing
│   ├── public/                # Static assets (Images, Icons)
│   ├── src/app/               # Next.js 14 App Router Pages
│   │   ├── account/           # User settings page
│   │   ├── dashboard/         # Progress stats page
│   │   ├── globals.css        # Global Tailwind & Custom Utilities
│   │   ├── layout.js          # Root layout
│   │   └── page.js            # Main Landing / App Interface
│   ├── package.json           # Node.js dependencies
│   ├── tailwind.config.js     # Tailwind design tokens
│   └── next.config.mjs        # Next.js build configurations
│
├── .env                       # Environment Variables
├── .gitignore                 # Git ignore rules
└── README.md                  # Project Overview
```
