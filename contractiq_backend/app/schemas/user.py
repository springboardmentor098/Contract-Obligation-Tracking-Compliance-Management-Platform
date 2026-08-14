# from pydantic import BaseModel, EmailStr


# class UserCreate(BaseModel):
#     full_name: str
#     email: EmailStr
#     role: str


# class UserResponse(BaseModel):
#     id: int
#     full_name: str
#     email: EmailStr
#     role: str
#     is_active: bool

#     class Config:
#         from_attributes = True


# from pydantic import BaseModel, EmailStr


# class UserCreate(BaseModel):
#     full_name: str
#     email: EmailStr
#     role: str
#     password: str


# class UserUpdate(BaseModel):
#     full_name: str
#     email: EmailStr
#     role: str
#     password: str
#     is_active: bool


# class UserResponse(BaseModel):
#     id: int
#     full_name: str
#     email: EmailStr
#     role: str
#     is_active: bool

#     class Config:
#         from_attributes = True



from pydantic import BaseModel, EmailStr

from app.core.roles import UserRole


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole
    password: str


class UserUpdate(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole
    password: str
    is_active: bool


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True