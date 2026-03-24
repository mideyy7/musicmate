from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

from app.core.database import Base, engine
from app.models import User, SpotifyToken, MusicProfile, Swipe, Match, Message, SharedPlaylist, PlaylistMember, WeeklyRecap, DailyTune, Reaction  # noqa: F401
from app.api.routes.auth import router as auth_router
from app.api.routes.spotify import router as spotify_router
from app.api.routes.match import router as match_router
from app.api.routes.chat import router as chat_router
from app.api.routes.playlist import router as playlist_router
from app.api.routes.posts import router as posts_router
from app.api.routes.feed import router as feed_router

# Create database tables
Base.metadata.create_all(bind=engine)

# SQLite column migrations — add new columns to existing tables without dropping data
from sqlalchemy import text
with engine.connect() as _conn:
    for _col, _type in [
        ("spotify_id", "VARCHAR"),
        ("spotify_url", "VARCHAR"),
        ("cover_image", "VARCHAR"),
        ("preview_url", "VARCHAR"),
    ]:
        try:
            _conn.execute(text(f"ALTER TABLE daily_tunes ADD COLUMN {_col} {_type}"))
            _conn.commit()
        except Exception:
            pass  # Column already exists

app = FastAPI(title="MusicMate API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(spotify_router)
app.include_router(match_router)
app.include_router(chat_router)
app.include_router(playlist_router)
app.include_router(posts_router)
app.include_router(feed_router)

# Static files for uploaded profile pictures
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
def root():
    return {"message": "MusicMate API is running"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
