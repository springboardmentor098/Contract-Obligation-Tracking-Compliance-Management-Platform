from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


# =========================
# CONTRACT CATEGORY
# =========================

ContractCategory = Literal[
    "Employment Contract",
    "Vendor Contract",
    "Service Agreement",
    "Lease Agreement",
    "Purchase Agreement",
    "Partnership Agreement",
    "Confidentiality Agreement"
]


# =========================
# CONTRACT STATUS
# =========================

ContractStatus = Literal[
    "Draft",
    "Under Review",
    "Approved",
    "Active",
    "Expired",
    "Terminated"
]


# =========================
# CREATE CONTRACT
# =========================

class ContractCreate(BaseModel):
    contract_number: str
    title: str
    category: ContractCategory
    description: str | None = None
    party_name: str
    start_date: date
    end_date: date


# =========================
# UPDATE CONTRACT
# =========================

class ContractUpdate(BaseModel):
    title: str | None = None
    category: ContractCategory | None = None
    description: str | None = None
    party_name: str | None = None
    start_date: date | None = None
    end_date: date | None = None


# =========================
# STATUS UPDATE
# =========================

class ContractStatusUpdate(BaseModel):
    status: ContractStatus


# =========================
# ASSIGN CONTRACT
# =========================

class ContractAssignment(BaseModel):
    assigned_to: int


# =========================
# RESPONSE
# =========================

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
    assigned_to: int | None

    reviewed_at: datetime | None
    approved_at: datetime | None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True