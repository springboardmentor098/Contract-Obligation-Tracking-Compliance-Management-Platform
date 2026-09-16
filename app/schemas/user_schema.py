from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: str
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: str
    email: EmailStr
    role: str
    is_active: bool = True


class PasswordChange(BaseModel):
    password: str


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True