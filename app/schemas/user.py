from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str  # для регистрации


class UserRead(UserBase):
    id: int
    avatar_url: Optional[str]
    is_admin: bool
    created_at: datetime
    attended_event_ids: List[int] = []

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int
