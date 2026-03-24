# Phase 1 — UoM SSO Authentication: Complete

## Backend (FastAPI)
config.py — Settings with allowed email domains
database.py — SQLite + SQLAlchemy setup
models/user.py — User model with academic fields + visibility toggles
schemas/user.py — Pydantic request/response schemas
services/auth.py — SSO simulation, JWT, password hashing
crud/user.py — Database operations
api/deps.py — Auth dependencies (JWT extraction)
api/routes/auth.py — 5 auth endpoints

## Frontend (React)
context/AuthContext.jsx — Auth state management
pages/LoginPage.jsx — SSO button + local login
pages/SSOPage.jsx — Email verification
pages/OnboardingPage.jsx — Academic info + password setup
pages/DashboardPage.jsx — Profile with edit + visibility toggles
components/ProtectedRoute.jsx — Auth guard
Dark theme with purple/music-app feel


## Verification Results: 12/12 tests passed
Non-UoM emails (gmail.com, oxford.ac.uk) rejected
First-time SSO flow works with academic data detection
JWT-based local login for returning users
Protected endpoints block unauthorized access
Visibility toggles for academic fields work
Duplicate signup prevention (409)
Both @manchester.ac.uk and @student.manchester.ac.uk accepted

# Phase 2 — Spotify Integration & Music Profile: Complete

## Backend (new/modified files)
config.py — Added SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
models/spotify.py — SpotifyToken model (access/refresh tokens, expiry)
models/music_profile.py — MusicProfile model (artists, genres, tracks, patterns as JSON)
schemas/spotify.py — Pydantic schemas for auth URL, callback, profile response
services/spotify.py — Full Spotify OAuth + API integration (auth URL, code exchange, token refresh, fetch artists/tracks/recent, profile builder)
crud/spotify.py — CRUD for tokens and music profile
api/routes/spotify.py — 6 endpoints: auth-url, callback, status, sync, profile, disconnect

## Frontend (new/modified files)
pages/SpotifyCallbackPage.jsx — Handles Spotify redirect, exchanges code, syncs profile
components/MusicProfile.jsx — Displays top artists grid, genre tags, recent tracks, listening summary
pages/DashboardPage.jsx — Updated with "Connect Spotify" button + music profile display
services/api.js — 6 new Spotify API functions
App.jsx — Added /spotify/callback route
App.css — Spotify green button, artist grid, genre tags, track list styles
Verification: 16/16 tests passed
Auth URL generates correctly with proper scopes
Status endpoint correctly reports connection state
Profile returns 404 when not synced, 200 when available
Sync blocked without connection
Invalid codes handled gracefully (400)
All endpoints require authentication
Disconnect cleans up tokens and profile
Phase 1 auth still works

## TODO
To activate Spotify OAuth:
Edit backend/.env and replace the placeholders:
SPOTIFY_CLIENT_ID=your_real_client_id
SPOTIFY_CLIENT_SECRET=your_real_client_secret
Also add http://localhost:5173/spotify/callback as a redirect URI in your Spotify Developer Dashboard.