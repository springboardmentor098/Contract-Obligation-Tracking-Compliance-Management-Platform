from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class RenewalCreate(BaseModel):
    contract_id: int
    renewal_date: date
    previous_expiry_date: date
    new_expiry_date: date
    assigned_to: int
    notes: Optional[str] = None


class RenewalUpdate(BaseModel):
    renewal_date: Optional[date] = None
    new_expiry_date: Optional[date] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None


class RenewalStatusUpdate(BaseModel):
    status: str


class RenewalResponse(BaseModel):
    id: int
    contract_id: int
    renewal_date: date
    previous_expiry_date: date
    new_expiry_date: date
    status: str
    assigned_to: Optional[int]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True