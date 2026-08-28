from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ContractCreate(BaseModel):
    title: str
    contract_number: str
    category: str
    description: str
    start_date: date
    end_date: date


class ContractUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ContractStatusUpdate(BaseModel):
    status: str


class ContractAssignment(BaseModel):
    assigned_to: int


class ContractResponse(BaseModel):
    id: int
    title: str
    contract_number: str
    category: str
    description: str
    start_date: date
    end_date: date
    status: str
    created_by: int
    assigned_to: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True