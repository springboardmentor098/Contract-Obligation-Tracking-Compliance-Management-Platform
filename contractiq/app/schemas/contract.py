from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.contract import ContractCategory, ContractStatus


class ContractCreate(BaseModel):
    title: str
    contract_number: str
    category: ContractCategory
    description: Optional[str] = None
    start_date: date
    end_date: date

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, v, info):
        start = info.data.get("start_date")
        if start and v <= start:
            raise ValueError("end_date must be after start_date")
        return v


class ContractUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[ContractCategory] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ContractStatusUpdate(BaseModel):
    status: ContractStatus


class ContractAssignmentUpdate(BaseModel):
    assigned_to: int


class ContractListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    contract_number: str
    category: ContractCategory
    status: ContractStatus
    end_date: date


class ContractResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    contract_number: str
    category: ContractCategory
    description: Optional[str] = None
    start_date: date
    end_date: date
    status: ContractStatus
    created_by: int
    assigned_to: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
