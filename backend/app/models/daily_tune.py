from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, JSON
from app.core.database import Base

class DailyTune(Base):
    __tablename__ = "daily_tunes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    song_name = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Reaction(Base):
    __tablename__ = "reactions"
    id = Column(Integer, primary_key=True, index=True)
    daily_tune_id = Column(Integer, ForeignKey("daily_tunes.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reaction_type = Column(String, nullable=False)  # "like", "dislike"
    created_at = Column(DateTime, default=datetime.utcnow)
