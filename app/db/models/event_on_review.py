from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base
from app.db.models.user import User


class EventOnReview(Base):
    __tablename__ = "events_on_review"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    event_date = Column(DateTime, nullable=False)
    category = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator_id = Column(Integer, ForeignKey("users.id"))

    # Связь с пользователем
    user = relationship("User", back_populates="events_on_review")
