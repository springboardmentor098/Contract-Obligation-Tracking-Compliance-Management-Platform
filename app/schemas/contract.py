from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ContractBase(BaseModel):
    title: str
    vendor_name: str
    contract_number: str
    start_date: date
    end_date: date
    status: Optional[str] = "active"


class ContractCreate(ContractBase):
    pass


class ContractResponse(ContractBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
