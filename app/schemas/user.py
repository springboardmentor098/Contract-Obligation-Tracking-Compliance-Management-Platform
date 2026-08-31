from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr


class UserRole(str, Enum):
    ADMINISTRATOR = "Administrator"
    LEGAL_MANAGER = "Legal Manager"
    COMPLIANCE_OFFICER = "Compliance Officer"
    CONTRACT_MANAGER = "Contract Manager"
    DEPARTMENT_HEAD = "Department Head"
    EMPLOYEE = "Employee"


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
