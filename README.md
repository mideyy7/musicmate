# MusicMate

A music-based social matching app for University of Manchester students. Connect with people who share your taste in music, chat through shared playlists, and discover what's playing across campus.

---

## Features

- **Music Matching** — Swipe on other students and match based on Spotify listening compatibility
- **Compatibility Scoring** — Algorithmic scoring based on shared artists, genres, and listening patterns
- **Chat** — Message your matches and share songs directly in conversation
- **Shared Playlists** — Collaborative playlists auto-created when you match
- **Daily Tunes** — Post one song per day and see what the whole campus is listening to
- **Campus Pulse** — Live feed of top songs, genre trends, and friend favourites across campus
- **UoM Authentication** — Sign in via University of Manchester CAS (Central Authentication Service) or email SSO

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, React Router v7, Vite |
| Backend | Python, FastAPI, SQLAlchemy |
| Database | PostgreSQL (Supabase) |
| Auth | JWT, UoM CAS, bcrypt |
| Music API | Spotify Web API, Last.fm |
| Hosting | Render (backend), Vercel (frontend) |

---

## Project Structure

```
musicmate/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/       # auth, spotify, match, chat, playlist, posts, feed
│   │   │   └── deps.py       # JWT auth dependency
│   │   ├── core/
│   │   │   ├── config.py     # Settings (reads from .env)
│   │   │   └── database.py   # SQLAlchemy engine + session
│   │   ├── crud/             # Database operations
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # Business logic (auth, spotify, CAS, compatibility, demo seed)
│   │   └── main.py           # FastAPI app entry point
│   ├── requirements.txt
│   └── .env                  # Local environment variables (not committed)
└── frontend/
    ├── public/
    │   └── _redirects        # SPA routing for Render static site
    ├── src/
    │   ├── components/       # NavBar, MiniPlayer, ProtectedRoute, etc.
    │   ├── context/          # AuthContext, SpotifyPlayerContext
    │   ├── pages/            # All page components
    │   └── services/
    │       └── api.js        # Centralised API client
    └── vite.config.js
```

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- A Spotify developer app ([create one here](https://developer.spotify.com/dashboard))

### Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env
cp .env.example .env  # then fill in your values

# Run the server
python -m app.main
# API available at http://127.0.0.1:8000
```

### Frontend

```bash
cd frontend

npm install
npm run dev
# App available at http://127.0.0.1:5173
```

The Vite dev server proxies `/api` requests to the backend automatically.

---

## Environment Variables

### Backend `.env`

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | JWT signing secret (use a long random string) | `openssl rand -hex 32` |
| `SPOTIFY_CLIENT_ID` | Spotify app client ID | from Spotify Dashboard |
| `SPOTIFY_CLIENT_SECRET` | Spotify app client secret | from Spotify Dashboard |
| `SPOTIFY_REDIRECT_URI` | Spotify OAuth callback URL | `https://yourapp.vercel.app/spotify/callback` |
| `LASTFM_API_KEY` | Last.fm API key (optional) | from Last.fm |
| `FORCE_MOCK_MODE` | Use mock Spotify data instead of real API | `true` / `false` |

### Frontend (set in Vercel/Render dashboard)

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `https://your-backend.onrender.com/api` |

---

## Deployment

### Backend — Render Web Service

1. Connect your GitHub repo to Render
2. **Build command:** `pip install -r requirements.txt`
3. **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Root directory:** `backend`
5. Add all backend environment variables in the Render dashboard

### Frontend — Vercel

1. Connect your GitHub repo to Vercel
2. **Framework preset:** Vite
3. **Root directory:** `frontend`
4. Add `VITE_API_URL` pointing to your Render backend URL in Vercel's environment settings
5. Vercel handles SPA routing automatically

> The `frontend/public/_redirects` file handles SPA routing if deployed on Render Static Sites instead.

---

## Authentication

### UoM CAS (Central Authentication Service)

Students authenticate via the University of Manchester CAS server. The flow:

1. Frontend calls `/api/auth/cas/initiate` — backend generates a one-time ticket stored in the database and returns a CAS redirect URL
2. User authenticates on the UoM CAS server
3. CAS redirects back to `/cas/callback?username=...&fullname=...`
4. Frontend calls `/api/auth/cas/complete` — backend verifies the ticket with UoM CAS server-to-server, creates/loads the user, returns a JWT

> Tickets are stored in PostgreSQL (not in-memory) so they survive server restarts on Render's free tier.

### Email SSO

An email-based signup flow for `@manchester.ac.uk` and `@student.manchester.ac.uk` addresses, with password authentication for returning users.

---

## Demo Mode

On first login, 14 demo students are automatically seeded for pitch/demo purposes:

- **6 pre-matched** — already matched with you, with chat messages and shared playlists
- **8 in the swipe feed** — appear as fresh candidates each session

Demo data is idempotent and resets swipe history on each login so the feed always has people to discover. Set `FORCE_MOCK_MODE=true` to use mock Spotify profiles instead of real API data.

---

## API Overview

| Prefix | Description |
|--------|-------------|
| `POST /api/auth/...` | Registration, login, CAS flow, profile updates |
| `GET/POST /api/spotify/...` | OAuth, music profile sync, search, playback token |
| `GET/POST /api/match/...` | Swipe feed, swipe action, match list |
| `GET/POST /api/chat/...` | Messages, unread counts, song search |
| `GET/POST /api/playlist/...` | Shared playlists, members, weekly recaps |
| `GET/POST /api/posts/...` | Daily tunes, reactions |
| `GET /api/feed/...` | Campus Pulse — top songs, genre trends, friend favourites |
