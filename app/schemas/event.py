from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum

class EventCategory(str, Enum):
    concert = "Концерт"
    sport = "Спорт"
    cinema = "Кино"
    other = "Другое"

class EventBase(BaseModel):
    title: str
    description: str
    event_date: datetime
    category: EventCategory
    image_url: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    category: Optional[EventCategory] = None
    image_url: Optional[str] = None
    is_approved: Optional[bool] = None  # 👈 здесь можно обновлять

class EventOut(EventBase):
    id: int
    created_at: datetime
    creator_id: int
    is_approved: bool

class EventRead(EventOut):
    participants: List[int] = []

    class Config:
        from_attributes = True
