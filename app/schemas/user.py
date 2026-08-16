from enum import Enum
from pydantic import BaseModel, ConfigDict


class UserRole(str, Enum):
    Administrator = "Administrator"
    Legal_Manager = "Legal Manager"
    Compliance_Officer = "Compliance Officer"
    Contract_Manager = "Contract Manager"
    Department_Head = "Department Head"
    Employee = "Employee"


class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    role: UserRole


class UserResponse(BaseModel):
    id: int
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