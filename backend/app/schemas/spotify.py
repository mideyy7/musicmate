from datetime import datetime

from pydantic import BaseModel


class SpotifyAuthURL(BaseModel):
    auth_url: str


class SpotifyCallbackRequest(BaseModel):
    code: str


class SpotifyStatusResponse(BaseModel):
    connected: bool
    spotify_user_id: str | None = None


class ArtistData(BaseModel):
    name: str
    spotify_id: str
    genres: list[str]
    image_url: str | None
    rank: int


class GenreData(BaseModel):
    genre: str
    count: int


class TrackData(BaseModel):
    name: str
    artist: str
    album: str
    image_url: str | None
    played_at: str | None = None
    spotify_id: str | None = None


class ListeningPatterns(BaseModel):
    total_artists: int = 0
    total_genres: int = 0
    top_genre: str | None = None
    avg_popularity: float = 0


class MusicProfileResponse(BaseModel):
    top_artists: list[ArtistData]
    top_genres: list[GenreData]
    recent_tracks: list[TrackData]
    listening_patterns: ListeningPatterns
    last_synced: datetime | None

    class Config:
        from_attributes = True
