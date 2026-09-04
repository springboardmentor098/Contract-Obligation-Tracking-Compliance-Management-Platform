from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


# ============================================================
# Obligation Types
# ============================================================

ObligationType = Literal[
    "Payment Obligation",
    "Delivery Commitment",
    "Reporting Requirement",
    "Renewal Condition",
    "Service Level Agreement",
    "Legal Compliance Requirement",
]


# ============================================================
# Obligation Status
# ============================================================

ObligationStatus = Literal[
    "Pending",
    "In Progress",
    "Completed",
    "Delayed",
    "Overdue",
]


# ============================================================
# Create Obligation Schema
# ============================================================

class ObligationCreate(BaseModel):
    contract_id: int
    title: str
    description: str | None = None
    obligation_type: ObligationType
    due_date: date
    assigned_to: int | None = None

    model_config = ConfigDict(
        extra="forbid"
    )


# ============================================================
# Update Obligation Schema
# ============================================================

class ObligationUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    obligation_type: ObligationType | None = None
    due_date: date | None = None
    assigned_to: int | None = None

    model_config = ConfigDict(
        extra="forbid"
    )


# ============================================================
# Update Obligation Status Schema
# ============================================================

class ObligationStatusUpdate(BaseModel):
    status: ObligationStatus

    model_config = ConfigDict(
        extra="forbid"
    )


# ============================================================
# Complete Obligation Schema
# ============================================================

class ObligationComplete(BaseModel):
    """
    Completion date is determined by the backend.
    The client does not provide the completion date.
    """

    model_config = ConfigDict(
        extra="forbid"
    )


# ============================================================
# Obligation Response Schema
# ============================================================

class ObligationResponse(BaseModel):
    id: int
    contract_id: int
    title: str
    description: str | None
    obligation_type: ObligationType
    due_date: date
    assigned_to: int | None
    status: ObligationStatus
    completion_date: date | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )