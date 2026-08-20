from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from app.models.contract import ContractCategory, ContractStatus

class ContractBase(BaseModel):
    title: str
    contract_number: str
    category: ContractCategory
    description: Optional[str] = None
    start_date: date
    end_date: date

class ContractCreate(ContractBase):
    pass 

#  NEW: Schema for updating contract details (PUT)
class ContractUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[ContractCategory] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

#  NEW: Schema for manually updating status (PATCH)
class ContractStatusUpdate(BaseModel):
    status: ContractStatus

#  NEW: Schema for assigning a contract
class ContractAssign(BaseModel):
    assigned_to: int


class ContractResponse(ContractBase):
    id: int
    status: ContractStatus
    created_by: int
    assigned_to: Optional[int] = None  # New field
    reviewed_at: Optional[datetime] = None  # New field
    approved_at: Optional[datetime] = None  # New field
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True