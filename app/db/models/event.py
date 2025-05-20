from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base
from app.db.models import comment
from sqlalchemy import ARRAY

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    event_date = Column(DateTime, nullable=False)
    category = Column(String, index=True)
    image_url = Column(ARRAY(String), nullable=True)
    is_approved = Column(Boolean, default=False)

    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User", back_populates="created_events")

    participants = relationship("User", secondary="user_event_association", back_populates="attended_events")
    comments = relationship("Comment", back_populates="event")
    favorited_by = relationship("Favorite", back_populates="event", cascade="all, delete-orphan")
