from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    student_id = Column(String, nullable=True)
    course = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    faculty = Column(String, nullable=True)
    show_course = Column(Boolean, default=True)
    show_year = Column(Boolean, default=True)
    show_faculty = Column(Boolean, default=True)
    spotify_email = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
