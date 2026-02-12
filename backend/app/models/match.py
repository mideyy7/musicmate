from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, JSON, String, ForeignKey, UniqueConstraint

from app.core.database import Base


class Swipe(Base):
    __tablename__ = "swipes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # "like" or "pass"
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "target_user_id", name="uq_user_target_swipe"),
    )


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    compatibility_score = Column(Float, nullable=False)
    breakdown = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
