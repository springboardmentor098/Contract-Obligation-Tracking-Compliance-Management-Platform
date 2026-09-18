from typing import Literal

from pydantic import BaseModel, EmailStr


# ---------------------------------------
# ContractIQ User Roles
# ---------------------------------------

UserRole = Literal[
    "Administrator",
    "Legal Manager",
    "Compliance Officer",
    "Contract Manager",
    "Department Head",
    "Employee"
]


# ---------------------------------------
# Create User Schema
# ---------------------------------------

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: UserRole


# ---------------------------------------
# User Response Schema
# ---------------------------------------

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True
