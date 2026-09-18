from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


RENEWAL_STATUSES = {
    "Upcoming",
    "In Progress",
    "Renewed",
    "Expired",
    "Cancelled",
}


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
            self.new_expiry_date is not None
            and self.renewal_date is not None
            and self.new_expiry_date < self.renewal_date
        ):
            raise ValueError(
                "new_expiry_date cannot be earlier than renewal_date"
            )

        if (
            self.renewal_date is not None
            and self.renewal_date > self.previous_expiry_date
        ):
            raise ValueError(
                "renewal_date cannot be later than previous_expiry_date"
            )

        return self


class RenewalUpdate(BaseModel):
    renewal_date: Optional[date] = None
    new_expiry_date: Optional[date] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.renewal_date and self.new_expiry_date:
            if self.new_expiry_date < self.renewal_date:
                raise ValueError(
                    "new_expiry_date cannot be earlier than renewal_date"
                )

        return self


class RenewalStatusUpdate(BaseModel):
    status: str = Field(...)

    @model_validator(mode="after")
    def validate_status(self):
        if self.status not in RENEWAL_STATUSES:
            raise ValueError(
                f"Invalid renewal status. Allowed values: "
                f"{', '.join(sorted(RENEWAL_STATUSES))}"
            )

        return self


class RenewalComplete(BaseModel):
    new_expiry_date: Optional[date] = None
    notes: Optional[str] = None


class RenewalResponse(BaseModel):
    id: int
    contract_id: int
    renewal_date: Optional[date]
    previous_expiry_date: date
    new_expiry_date: Optional[date]
    status: str
    assigned_to: Optional[int]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UpcomingRenewalResponse(BaseModel):
    contract_id: int
    renewal_id: Optional[int]
    expiry_date: date
    days_remaining: int
    status: str