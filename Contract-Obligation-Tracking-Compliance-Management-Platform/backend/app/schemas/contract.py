from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


# ============================================================
# Contract Categories
# ============================================================

ContractCategory = Literal[
    "Employment Contract",
    "Vendor Contract",
    "Service Agreement",
    "Lease Agreement",
    "Purchase Agreement",
    "Partnership Agreement",
    "Confidentiality Agreement",
]


# ============================================================
# Contract Status
# ============================================================

ContractStatus = Literal[
    "Draft",
    "Under Review",
    "Approved",
    "Active",
    "Expired",
    "Terminated",
]


# ============================================================
# Create Contract Schema
# ============================================================

class ContractCreate(BaseModel):
    title: str
    contract_number: str
    category: ContractCategory
    description: str | None = None
    start_date: date
    end_date: date

    model_config = ConfigDict(
        extra="forbid"
    )

# ============================================================
# Update Contract Schema
# ============================================================

class ContractUpdate(BaseModel):
    title: str | None = None
    category: ContractCategory | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: ContractStatus | None = None


# ============================================================
# Contract Response Schema
# ============================================================

class ContractResponse(BaseModel):
    id: int
    title: str
    contract_number: str
    category: ContractCategory
    description: str | None
    start_date: date
    end_date: date
    status: ContractStatus
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)