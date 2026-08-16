from pydantic import BaseModel


# Request schema - Used while creating a new user
class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    role: str


# Response schema - Returned to the client
class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


# Request schema - Used while updating an existing user
class UserUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    password: str | None = None
    role: str | None = None


# Request schema - Used while logging in
class LoginRequest(BaseModel):
    email: str
    password: str