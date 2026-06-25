<div align="center">
  <img src="https://via.placeholder.com/150x150.png?text=Lingofy+Logo" alt="Lingofy Logo" width="150" height="150" />
  <h1>Lingofy</h1>
  <p><strong>Next-Generation AI Language Learning powered by Spotify</strong></p>

  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com/)
  [![AI](https://img.shields.io/badge/AI-Groq%20%7C%20OpenRouter-orange.svg)]()
</div>

---

## 🌟 Introduction

Lingofy is an innovative language-learning platform that seamlessly integrates with your **Spotify** account. By combining the power of your favorite music with state-of-the-art AI (Groq & OpenRouter), Lingofy transforms passive listening into an active, highly engaging language mastery experience.

## ❗ The Problem

Traditional language learning apps rely on repetitive flashcards, artificial dialogues, and isolated grammar exercises. Users often lose motivation because the context is dry and irrelevant to their daily lives. Furthermore, mastering pronunciation and shadowing requires expensive human tutors.

## 💡 The Solution

Lingofy turns the music you already listen to into personalized language lessons. It syncs real-time lyrics, provides instant high-quality translations using Llama-3, analyzes word morphology, and offers a **Shadowing Mode** and **Pronunciation Coach** to practice speaking—all dynamically generated on the fly.

---

## ✨ Features

- **🎵 Spotify Integration:** Play, pause, and sync lyrics directly from your active Spotify session.
- **🎤 Shadowing Mode:** Karaoke-style interface designed for language learners to repeat after the singer.
- **🗣️ Pronunciation Coach:** Record your voice and get instant phoneme-level feedback via Whisper AI and our custom scoring algorithm.
- **🧠 Word Learning:** Click any word to instantly view its dictionary definition, contextual translation, and frequency.
- **🇹🇷 Contextual Translation:** Uses Groq (LLaMA-3 70B) for natural, poetic translations of lyrics without breaking API limits (cached for 24h).
- **📈 Progress Dashboard:** Track your daily streaks, vocabulary mastery, and CEFR level progression.
- **💳 Tiered Memberships:** FREE, PRO, and MASTER tiers handling feature access limits via an integrated plan manager.

---

## 🏗️ Architecture

Lingofy uses a decoupled Client-Server architecture:
- **Frontend:** Next.js (React 18), TailwindCSS, Context API.
- **Backend:** Python FastAPI, SQLite, httpx, asyncio.
- **AI Layer:** Factory Pattern for Model Providers (Groq, OpenRouter), structured JSON parsing.
- **Cache:** In-memory TTL LRU Cache for translations and dictionary endpoints.

For a deep dive into the architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 🛠️ Tech Stack

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Styling:** Tailwind CSS + Vanilla CSS (Dynamic Glassmorphism)
- **State Management:** React Hooks + Context API
- **Audio:** Web Audio API (MediaRecorder)

### Backend
- **Framework:** FastAPI
- **Database:** SQLite3 (with custom schema migrations)
- **Authentication:** JWT (HttpOnly Cookies), OAuth2 (Spotify)
- **AI Integration:** Groq SDK, OpenRouter (Llama 3, OpenAI, Whisper)
- **Utilities:** Deep Translator (Fallback), Pydantic

For the full list, see [TECH_STACK.md](TECH_STACK.md).

---

## 📂 Folder Structure

```text
C:\Projeler\SpotifyBenzeri
├── backend/
│   ├── core/         # Config, Database, Providers, Caching
│   ├── routes/       # API Endpoints (Auth, Spotify, Lyrics, Chat)
│   ├── main.py       # FastAPI Entrypoint
│   └── data/         # SQLite Database
├── frontend/
│   ├── src/app/      # Next.js Pages
│   ├── components/   # React UI Components
│   ├── lib/          # API Client & Utils
│   └── public/       # Static Assets
└── README.md
```
*See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed explanations.*

---

## 🚀 Installation & Running Locally

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- Spotify Developer Account (Client ID & Secret)
- Groq / OpenRouter API Keys

### Environment Variables
Create a `.env` in the project root:
```env
# Backend & AI
JWT_SECRET=your_super_secret_key
GROQ_API_KEY=gsk_...
OPENROUTER_API_KEY=sk-or-v1-...
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:3000/callback

# Frontend
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### 1. Start the Backend
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --host 127.0.0.1
```

### 2. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:3000`.

---

## 🐳 Docker & Production Build

To run Lingofy in a production environment using Docker and Nginx, refer to the [DEPLOYMENT.md](DEPLOYMENT.md) guide.

---

## 🗺️ Roadmap

We are constantly improving Lingofy. Some upcoming features:
- **Mobile Apps:** React Native / Expo ports.
- **Enterprise/Education:** Teacher dashboards for language schools.
- **Offline Mode:** Download lyrics and cache audio.

See [ROADMAP.md](ROADMAP.md) for full details.

---

## 📜 Documentation Index

Please refer to the following documents for comprehensive system details:
- 🏗️ [Architecture](ARCHITECTURE.md)
- 🧠 [AI Infrastructure](AI.md)
- 🔌 [API Reference](API.md)
- 🗄️ [Database Schema](DATABASE.md)
- 🚀 [Deployment Guide](DEPLOYMENT.md)
- 🤝 [Contributing Guidelines](CONTRIBUTING.md)
- 🔒 [Security Overview](SECURITY.md)
- 📍 [Roadmap](ROADMAP.md)
- 📝 [Changelog](CHANGELOG.md)
- 💼 [Investor Overview](INVESTOR_OVERVIEW.md)
- 💻 [Tech Stack](TECH_STACK.md)
- 📁 [Project Structure](PROJECT_STRUCTURE.md)
- 🚶 [Walkthrough (For Devs)](WALKTHROUGH.md)
- 📦 [Product Overview](PRODUCT.md)

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ✉️ Contact

For business inquiries, enterprise licenses, or partnerships, please reach out via GitHub Issues or contact the maintainer directly.
