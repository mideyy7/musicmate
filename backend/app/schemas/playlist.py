from datetime import date, datetime

from pydantic import BaseModel


class PlaylistTrack(BaseModel):
    track_name: str
    artist: str
    album: str | None = None
    image_url: str | None = None
    spotify_url: str | None = None
    spotify_id: str
    added_by: int | None = None
    added_at: str | None = None


class AddTrackRequest(BaseModel):
    track_name: str
    artist: str
    album: str | None = None
    image_url: str | None = None
    spotify_url: str | None = None
    spotify_id: str


class CreatePlaylistRequest(BaseModel):
    name: str
    description: str | None = None
    match_id: int | None = None
    member_ids: list[int] | None = None


class AddMemberRequest(BaseModel):
    user_id: int


class PlaylistMemberResponse(BaseModel):
    user_id: int
    display_name: str
    role: str

    class Config:
        from_attributes = True


class PlaylistResponse(BaseModel):
    id: int
    name: str
    description: str | None
    playlist_type: str
    match_id: int | None
    spotify_playlist_id: str | None
    track_count: int
    member_count: int
    tracks: list[PlaylistTrack]
    members: list[PlaylistMemberResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlaylistSummaryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    playlist_type: str
    match_id: int | None
    track_count: int
    member_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class WeeklyRecapResponse(BaseModel):
    id: int
    playlist_id: int
    week_start: date
    recap_data: dict
    created_at: datetime

    class Config:
        from_attributes = True
