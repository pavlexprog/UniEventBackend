from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel



class UserBase(BaseModel):
    username: str

# class UserOut(BaseModel):
#     id: int
#     first_name: str
#     last_name: str
#     avatar_url: Optional[str]
#     total_events: Optional[int] = 0

#     class Config:
#         from_attributes = True

class UserCreate(UserBase):
    password: str  # для регистрации


class UserRead(UserBase):
    id: int
    avatar_url: Optional[str]
    is_admin: bool
    created_at: datetime
    attended_event_ids: List[int] = []
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int
