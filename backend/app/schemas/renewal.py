from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RenewalCreate(BaseModel):
    contract_id: UUID
    renewal_date: date | None = None
    previous_expiry_date: date | None = None
    new_expiry_date: date | None = None
    assigned_to: UUID
    notes: str | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.renewal_date is not None
            and self.previous_expiry_date is not None
            and self.renewal_date > self.previous_expiry_date
        ):
            raise ValueError(
                "Renewal date cannot be later than the previous expiry date"
            )

        if (
            self.renewal_date is not None
            and self.new_expiry_date is not None
            and self.new_expiry_date < self.renewal_date
        ):
            raise ValueError(
                "New expiry date cannot be earlier than the renewal date"
            )

        return self


class RenewalUpdate(BaseModel):
    renewal_date: date | None = None
    new_expiry_date: date | None = None
    assigned_to: UUID | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.renewal_date is not None
            and self.new_expiry_date is not None
            and self.new_expiry_date < self.renewal_date
        ):
            raise ValueError(
                "New expiry date cannot be earlier than the renewal date"
            )

        return self


class RenewalStatusUpdate(BaseModel):
    status: str = Field(..., min_length=1, max_length=50)


class RenewalComplete(BaseModel):
    new_expiry_date: date


class RenewalResponse(BaseModel):
    id: UUID
    contract_id: UUID
    renewal_date: date | None
    previous_expiry_date: date | None
    new_expiry_date: date | None
    status: str
    assigned_to: UUID
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)