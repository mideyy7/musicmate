from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.database import Base, engine
from app.models import User, SpotifyToken, MusicProfile, Swipe, Match, Message, SharedPlaylist, PlaylistMember, WeeklyRecap  # noqa: F401
from app.api.routes.auth import router as auth_router
from app.api.routes.spotify import router as spotify_router
from app.api.routes.match import router as match_router
from app.api.routes.chat import router as chat_router
from app.api.routes.playlist import router as playlist_router

# Create database tables
Base.metadata.create_all(bind=engine)

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
