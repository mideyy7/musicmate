from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint

from app.core.database import Base


class SharedPlaylist(Base):
    __tablename__ = "shared_playlists"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    spotify_playlist_id = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    playlist_type = Column(String, default="match")  # "match" or "group"
    tracks = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PlaylistMember(Base):
    __tablename__ = "playlist_members"

    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("shared_playlists.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, default="editor")  # "owner" or "editor"
    joined_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("playlist_id", "user_id", name="uq_playlist_member"),
    )


class WeeklyRecap(Base):
    __tablename__ = "weekly_recaps"

    id = Column(Integer, primary_key=True, index=True)
    playlist_id = Column(Integer, ForeignKey("shared_playlists.id"), nullable=False)
    week_start = Column(Date, nullable=False)
    recap_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
