from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.core.rbac import UserRole


class UserCreate(BaseModel):
    full_name: str
    email: str
    role: UserRole
    password: str


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    role: UserRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: UserRole