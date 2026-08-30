from datetime import date, datetime

from pydantic import BaseModel, Field


class RenewalCreate(BaseModel):
    contract_id: int
    renewal_date: date
    previous_expiry_date: date
    new_expiry_date: date | None = None
    assigned_to: int
    notes: str | None = None


class RenewalUpdate(BaseModel):
    renewal_date: date | None = None
    new_expiry_date: date | None = None
    assigned_to: int | None = None
    notes: str | None = None


class RenewalStatusUpdate(BaseModel):
    status: str


class RenewalComplete(BaseModel):
    new_expiry_date: date


class RenewalResponse(BaseModel):
    id: int
    contract_id: int
    renewal_date: date
    previous_expiry_date: date
    new_expiry_date: date | None
    status: str
    assigned_to: int
    notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True