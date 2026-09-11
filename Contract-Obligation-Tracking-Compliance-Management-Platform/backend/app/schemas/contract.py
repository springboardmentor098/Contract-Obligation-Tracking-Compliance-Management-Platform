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
    """
    Used only for updating contract information.

    Status must NOT be changed through this schema.
    Status changes are handled by dedicated workflow APIs.
    """

    title: str | None = None
    category: ContractCategory | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None

    model_config = ConfigDict(
        extra="forbid"
    )


# ============================================================
# Contract Status Update Schema
# ============================================================

class ContractStatusUpdate(BaseModel):
    status: ContractStatus

    model_config = ConfigDict(
        extra="forbid"
    )


# ============================================================
# Contract Assignment Schema
# ============================================================

class ContractAssignment(BaseModel):
    assigned_to: int

    model_config = ConfigDict(
        extra="forbid"
    )


class ContractAssignmentResponse(BaseModel):
    message: str
    contract_id: int
    assigned_to: int
    contract: "ContractResponse"


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

    # Workflow
    status: ContractStatus

    # Users
    created_by: int
    assigned_to: int | None

    # Timestamps
    reviewed_at: datetime | None
    approved_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
