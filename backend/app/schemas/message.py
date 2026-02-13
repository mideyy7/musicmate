from datetime import datetime

from pydantic import BaseModel


class SongShareData(BaseModel):
    track_name: str
    artist: str
    album: str | None = None
    image_url: str | None = None
    spotify_url: str | None = None
    spotify_id: str | None = None


class SendMessageRequest(BaseModel):
    content: str
    message_type: str = "text"  # "text" or "song_share"
    song_data: SongShareData | None = None


class MessageResponse(BaseModel):
    id: int
    match_id: int
    sender_id: int
    content: str
    message_type: str
    song_data: SongShareData | None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UnreadCountResponse(BaseModel):
    total: int
    by_match: dict[int, int]


class SongSearchResult(BaseModel):
    track_name: str
    artist: str
    album: str
    image_url: str | None = None
    spotify_url: str | None = None
    spotify_id: str
