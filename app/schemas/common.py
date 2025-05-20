# common.py
from pydantic import BaseModel
from typing import Optional

class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    avatar_url: Optional[str]
    total_events: Optional[int] = 0

    class Config:
        from_attributes = True
