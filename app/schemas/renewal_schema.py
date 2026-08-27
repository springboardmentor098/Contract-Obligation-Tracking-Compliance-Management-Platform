from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


# ============================================================
# RENEWAL STATUSES
# ============================================================

RENEWAL_STATUSES = {
    "Upcoming",
    "In Progress",
    "Renewed",
    "Expired",
    "Cancelled",
}


# ============================================================
# CREATE RENEWAL
# ============================================================

class RenewalCreate(BaseModel):
    contract_id: int
    renewal_date: date
    previous_expiry_date: date
    new_expiry_date: date | None = None
    assigned_to: int | None = None
    notes: str | None = None


# ============================================================
# UPDATE RENEWAL
# ============================================================

class RenewalUpdate(BaseModel):
    renewal_date: date
    new_expiry_date: date | None = None
    assigned_to: int | None = None
    notes: str | None = None


# ============================================================
# UPDATE RENEWAL STATUS
# ============================================================

class RenewalStatusUpdate(BaseModel):
    status: str


# ============================================================
# COMPLETE / RENEW RENEWAL
# ============================================================

class RenewalComplete(BaseModel):
    new_expiry_date: date


# ============================================================
# RENEWAL RESPONSE
# ============================================================

class RenewalResponse(BaseModel):
    id: int
    contract_id: int
    renewal_date: date
    previous_expiry_date: date
    new_expiry_date: date | None
    status: str
    assigned_to: int | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)