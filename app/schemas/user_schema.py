from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    role: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    avatar_url: Optional[str] = None
    preferences: Optional[dict] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool
    avatar_url: Optional[str] = None
    last_login: Optional[datetime] = None
    preferences: Optional[dict] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True