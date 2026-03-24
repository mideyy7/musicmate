from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.core.database import Base


class CASTicket(Base):
    __tablename__ = "cas_tickets"

    id = Column(Integer, primary_key=True, index=True)
    csticket = Column(String, unique=True, index=True, nullable=False)
    callback_url = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
