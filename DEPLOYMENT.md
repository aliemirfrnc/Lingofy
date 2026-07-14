# Deployment Guide

This guide outlines how to deploy Lingofy to a production environment.

## 1. Environment Preparation
Ensure you have a Linux server (Ubuntu 22.04 LTS recommended) or a Windows Server environment.

### Prerequisites
- Node.js (v18+)
- Python (3.14+)
- Nginx
- PM2 (for Node.js process management)

## 2. Environment Variables (.env)
Create a `.env` file in the root directory and ensure it is heavily restricted (`chmod 600`).
```env
ENVIRONMENT=production
JWT_SECRET=your_super_secure_random_string
GROQ_API_KEY=gsk_...
OPENROUTER_API_KEY=sk-or-v1-...
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
```

## 3. Backend Deployment
1. Navigate to the backend directory.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI application using Gunicorn with Uvicorn workers:
   ```bash
   gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
   ```
   *(Note: Use systemd to manage this process in a real production environment).*

## 4. Frontend Deployment
1. Navigate to the frontend directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Build the Next.js application:
   ```bash
   npm run build
   ```
4. Start the production server using PM2:
   ```bash
   npm install -g pm2
   pm2 start npm --name "lingofy-frontend" -- start
   ```

## 5. Nginx Reverse Proxy & HTTPS
Configure Nginx to route traffic to the frontend and backend, and secure it with SSL (Let's Encrypt).

```nginx
server {
    listen 80;
    server_name lingofy.io www.lingofy.io;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name lingofy.io www.lingofy.io;

    ssl_certificate /etc/letsencrypt/live/lingofy.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/lingofy.io/privkey.pem;

    # Route to Frontend
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Route to Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 6. Docker (Alternative)
A `docker-compose.yml` is planned for Sprint 2 to containerize the application along with PostgreSQL and Redis.
