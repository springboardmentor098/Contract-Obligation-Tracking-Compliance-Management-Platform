# app/schemas/obligation.py

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


# -----------------------------
# Create Obligation
# -----------------------------
class ObligationCreate(BaseModel):
    contract_id: int
    title: str
    description: str | None = None
    obligation_type: str
    due_date: date
    assigned_to: int


# -----------------------------
# Update Obligation
# -----------------------------
class ObligationUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    obligation_type: str | None = None
    due_date: date | None = None
    assigned_to: int | None = None


# -----------------------------
# Update Obligation Status
# -----------------------------
class ObligationStatusUpdate(BaseModel):
    status: str


# -----------------------------
# Complete Obligation
# -----------------------------
class ObligationComplete(BaseModel):
    pass


# -----------------------------
# Response
# -----------------------------
class ObligationResponse(BaseModel):
    id: int
    contract_id: int
    title: str
    description: str | None
    obligation_type: str
    due_date: date
    assigned_to: int
    status: str
    completion_date: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)