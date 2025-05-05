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


class EventCreate(EventBase):
    pass


class EventUpdate(EventBase):
    pass


class EventOut(EventBase):
    id: int
    created_at: datetime
    creator_id: int


class EventRead(EventBase):
    id: int
    created_at: datetime
    participants: List[int] = []
    image_url: Optional[str]

    class Config:
        from_attributes = True
