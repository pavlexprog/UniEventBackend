from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
from app.schemas.common import UserOut
from pydantic import ConfigDict
# from app.schemas.user import UserOut


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
    image_url: Optional[List[str]] = None


class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    category: Optional[EventCategory] = None
    image_url: Optional[List[str]] = None
    is_approved: Optional[bool] = None  # 👈 здесь можно обновлять

class EventOut(EventBase):
    id: int
    created_at: datetime
    creator_id: int
    is_approved: bool
    participants_count: Optional[int] = 0
    is_favorite: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)

class EventRead(EventOut):
    participants: List[UserOut] = []
    creator: Optional[UserOut] = None
    joined: Optional[bool] = False
    

    model_config = ConfigDict(from_attributes=True)
