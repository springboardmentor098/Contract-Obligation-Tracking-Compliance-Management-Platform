from pydantic import BaseModel

class UserBase(BaseModel):
    full_name: str
    email: str
    role: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str   # plain password input

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True  # ✅ replaces orm_mode in Pydantic v2


