# SpotifyBenzeri (Spotify-like Platform)

![SpotifyBenzeri](5e04ca37-fbd0-4923-808b-1a7e0e823ede.png)

## Project Overview
SpotifyBenzeri is a high-performance, modern web application that mimics the core functionalities of Spotify. It features robust user authentication, music streaming capabilities, a dynamic frontend, and AI-powered recommendations. The project is designed with scalability and performance in mind, ensuring a seamless experience for users.

## Architecture
The application is built using a modern, decoupled architecture:
- **Frontend**: A React-based application (Next.js) providing a responsive and interactive user interface.
- **Backend**: A Python FastAPI service handling business logic, user authentication, and data management.
- **Database**: SQLite (with WAL mode enabled) for lightweight, fast, and concurrent data access during development and early production.
- **AI Integrations**: Integrated with Gemini, Groq, and OpenRouter for intelligent features.

For more detailed architectural diagrams and decisions, refer to `ARCHITECTURE.md` and `TECHNICAL_ARCHITECTURE.md`.

## Installation

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- Git

### Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd SpotifyBenzeri
   ```

2. Setup Backend:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Setup Frontend:
   ```bash
   cd frontend
   npm install
   ```

## Development

To run the application locally:

1. **Start the Backend**:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. **Start the Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

Access the frontend at `http://localhost:3000` and the API documentation at `http://localhost:8000/docs`.

## Environment Variables

The project requires specific environment variables to function properly. 
Do **NOT** commit real API keys to version control.

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Fill in the required values in `.env`:
   - `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `GROQ_API_KEY`
   - `JWT_SECRET` (Must be at least 32 characters)
   - `SPOTIFY_CLIENT_ID` & `SPOTIFY_CLIENT_SECRET`

## Testing

The repository contains a suite of tests to ensure reliability:
- **Unit & Integration Tests**: Run using `pytest` in the backend directory.
  ```bash
  pytest tests/
  ```
- **Performance & Stress Tests**: Check the `scripts/` folder for `db_stress.py` and `locustfile.py` to simulate high load.

## Security

Security is a primary concern:
- **JWT Authentication**: Short-lived access tokens and secure refresh tokens.
- **Secret Management**: All secrets are loaded from `.env` and excluded from Git via `.gitignore`.
- **CORS Policy**: Configured to only allow trusted origins.

If you discover a security vulnerability, please refer to `SECURITY.md` for reporting guidelines.

## Production Notes

Before deploying to production, ensure:
1. **Strong Secrets**: Generate a strong `JWT_SECRET` (e.g., using `openssl rand -hex 32`).
2. **Environment Variables**: Set all required production environment variables.
3. **Database**: If migrating away from SQLite, ensure connection strings are updated.
4. **Build**: Build the frontend for production (`npm run build`).

Review `DEPLOYMENT.md` for detailed production deployment instructions.
