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