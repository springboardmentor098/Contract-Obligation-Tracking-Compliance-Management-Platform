from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


# =========================
# RENEWAL STATUS
# =========================

RenewalStatus = Literal[
    "Upcoming",
    "In Progress",
    "Renewed",
    "Expired",
    "Cancelled"
]


# =========================
# CREATE RENEWAL
# =========================

class RenewalCreate(BaseModel):
    contract_id: int
    renewal_date: date
    previous_expiry_date: date
    new_expiry_date: date | None = None
    assigned_to: int
    notes: str | None = None


# =========================
# UPDATE RENEWAL
# =========================

class RenewalUpdate(BaseModel):
    renewal_date: date | None = None
    new_expiry_date: date | None = None
    assigned_to: int | None = None
    notes: str | None = None


# =========================
# UPDATE RENEWAL STATUS
# =========================

class RenewalStatusUpdate(BaseModel):
    status: RenewalStatus


# =========================
# RENEWAL RESPONSE
# =========================

class RenewalResponse(BaseModel):
    id: int
    contract_id: int
    renewal_date: date
    previous_expiry_date: date
    new_expiry_date: date | None
    status: RenewalStatus
    assigned_to: int
    notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True