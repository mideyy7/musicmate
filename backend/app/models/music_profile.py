from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class MusicProfile(Base):
    __tablename__ = "music_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    top_artists = Column(JSON, default=list)
    top_genres = Column(JSON, default=list)
    recent_tracks = Column(JSON, default=list)
    listening_patterns = Column(JSON, default=dict)
    last_synced = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="music_profile")
