from typing import Optional
from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class UserAuthInfo(BaseModel):
    id: int
    email: str
    name: str
    role: str
    avatar_url: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
    user: Optional[UserAuthInfo] = None