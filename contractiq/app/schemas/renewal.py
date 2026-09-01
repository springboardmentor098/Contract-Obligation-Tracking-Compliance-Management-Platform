from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.renewal import RenewalStatus


class RenewalCreate(BaseModel):
    contract_id: int
    renewal_date: date
    previous_expiry_date: date
    new_expiry_date: date
    assigned_to: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("new_expiry_date")
    @classmethod
    def new_expiry_after_renewal_date(cls, v, info):
        renewal_date = info.data.get("renewal_date")
        if renewal_date and v <= renewal_date:
            raise ValueError("new_expiry_date must be after renewal_date")
        return v


class RenewalUpdate(BaseModel):
    renewal_date: Optional[date] = None
    new_expiry_date: Optional[date] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None


class RenewalStatusUpdate(BaseModel):
    status: RenewalStatus


class RenewalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contract_id: int
    renewal_date: date
    previous_expiry_date: date
    new_expiry_date: date
    status: RenewalStatus
    assigned_to: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
