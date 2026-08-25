from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


# =========================
# OBLIGATION TYPES
# =========================

ObligationType = Literal[
    "Payment Obligation",
    "Delivery Commitment",
    "Reporting Requirement",
    "Renewal Condition",
    "Service Level Agreement",
    "Legal Compliance Requirement"
]


# =========================
# OBLIGATION STATUS
# =========================

ObligationStatus = Literal[
    "Pending",
    "In Progress",
    "Completed",
    "Delayed",
    "Overdue"
]


# =========================
# CREATE OBLIGATION
# =========================

class ObligationCreate(BaseModel):
    contract_id: int
    title: str
    description: str | None = None
    obligation_type: ObligationType
    due_date: date
    assigned_to: int


# =========================
# UPDATE OBLIGATION
# =========================

class ObligationUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    obligation_type: ObligationType | None = None
    due_date: date | None = None
    assigned_to: int | None = None


# =========================
# UPDATE STATUS
# =========================

class ObligationStatusUpdate(BaseModel):
    status: ObligationStatus


# =========================
# RESPONSE
# =========================

class ObligationResponse(BaseModel):
    id: int
    contract_id: int
    title: str
    description: str | None
    obligation_type: ObligationType
    due_date: date
    assigned_to: int
    status: ObligationStatus
    completion_date: date | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True