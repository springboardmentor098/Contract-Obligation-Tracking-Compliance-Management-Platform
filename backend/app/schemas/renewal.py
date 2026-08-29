from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class RenewalCreate(BaseModel):
    contract_id: int
    renewal_date: Optional[date] = None
    previous_expiry_date: date
    new_expiry_date: Optional[date] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("new_expiry_date")
    @classmethod
    def validate_new_expiry_date(cls, value, info):
        renewal_date = info.data.get("renewal_date")

        if value and renewal_date and value < renewal_date:
            raise ValueError(
                "New expiry date cannot be earlier than renewal date"
            )

        return value


class RenewalUpdate(BaseModel):
    renewal_date: Optional[date] = None
    new_expiry_date: Optional[date] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None

    @field_validator("new_expiry_date")
    @classmethod
    def validate_new_expiry_date(cls, value, info):
        renewal_date = info.data.get("renewal_date")

        if value and renewal_date and value < renewal_date:
            raise ValueError(
                "New expiry date cannot be earlier than renewal date"
            )

        return value


class RenewalStatusUpdate(BaseModel):
    status: str


class RenewalRenew(BaseModel):
    new_expiry_date: date


class RenewalOut(BaseModel):
    id: int
    contract_id: int
    renewal_date: Optional[date] = None
    previous_expiry_date: date
    new_expiry_date: Optional[date] = None
    status: str
    assigned_to: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)