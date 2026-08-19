from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


ContractCategory = Literal[
    "Employment Contract",
    "Vendor Contract",
    "Service Agreement",
    "Lease Agreement",
    "Purchase Agreement",
    "Partnership Agreement",
    "Confidentiality Agreement"
]


ContractStatus = Literal[
    "Draft",
    "Under Review",
    "Approved",
    "Active",
    "Expired",
    "Terminated"
]


class ContractCreate(BaseModel):
    contract_number: str
    title: str
    category: ContractCategory
    description: str | None = None
    party_name: str
    start_date: date
    end_date: date


class ContractResponse(BaseModel):
    id: int
    contract_number: str
    title: str
    category: ContractCategory
    description: str | None
    party_name: str
    start_date: date
    end_date: date
    status: ContractStatus
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContractUpdate(BaseModel):
    title: str | None = None
    category: ContractCategory | None = None
    description: str | None = None
    party_name: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: ContractStatus | None = None