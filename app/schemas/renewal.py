# app/schemas/renewal.py

from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class RenewalCreate(BaseModel):
    contract_id: int
    renewal_date: date
    new_expiry_date: date | None = None
    status: str
    notes: str | None = None
    approved_by: int | None = None


class RenewalResponse(BaseModel):
    id: int
    contract_id: int
    renewal_date: date
    new_expiry_date: date | None
    status: str
    notes: str | None
    approved_by: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
