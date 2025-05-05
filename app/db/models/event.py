from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base
from app.db.models import comment


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    creator_id = Column(Integer, nullable=False)
    event_date = Column(DateTime, nullable=False)
    category = Column(String, index=True)
    image_url = Column(String, nullable=True)
    is_approved = Column(Boolean, default=False)

    participants = relationship(
        "User", secondary="user_event_association", back_populates="attended_events")
    comments = relationship("Comment", back_populates="event")
