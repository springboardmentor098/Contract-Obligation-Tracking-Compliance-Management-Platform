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

# Used for POST /contracts (Notice we don't ask for 'status' or 'created_by' here!)
class ContractCreate(ContractBase):
    pass 

# Used for returning data back to the user
class ContractResponse(ContractBase):
    id: int
    status: ContractStatus
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True