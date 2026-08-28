from datetime import date, datetime
from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


RenewalStatus = Literal[
    "Upcoming",
    "In Progress",
    "Renewed",
    "Expired",
    "Cancelled"
]


class RenewalCreate(BaseModel):
    contract_id: int
    renewal_date: Optional[date] = None
    previous_expiry_date: date
    new_expiry_date: Optional[date] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.renewal_date
            and self.new_expiry_date
            and self.new_expiry_date < self.renewal_date
        ):
            raise ValueError(
                "New expiry date cannot be earlier than renewal date"
            )

        return self


class RenewalUpdate(BaseModel):
    renewal_date: Optional[date] = None
    new_expiry_date: Optional[date] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.renewal_date
            and self.new_expiry_date
            and self.new_expiry_date < self.renewal_date
        ):
            raise ValueError(
                "New expiry date cannot be earlier than renewal date"
            )

        return self


class RenewalStatusUpdate(BaseModel):
    status: RenewalStatus


class RenewalComplete(BaseModel):
    renewal_date: Optional[date] = None
    new_expiry_date: Optional[date] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.renewal_date
            and self.new_expiry_date
            and self.new_expiry_date < self.renewal_date
        ):
            raise ValueError(
                "New expiry date cannot be earlier than renewal date"
            )

        return self


class RenewalResponse(BaseModel):
    id: int
    contract_id: int
    renewal_date: Optional[date] = None
    previous_expiry_date: date
    new_expiry_date: Optional[date] = None
    status: RenewalStatus
    assigned_to: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)