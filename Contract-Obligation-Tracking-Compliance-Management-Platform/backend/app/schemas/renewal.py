from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


RenewalStatus = Literal[
    "Upcoming",
    "In Progress",
    "Renewed",
    "Expired",
    "Cancelled",
]


class RenewalCreate(BaseModel):
    contract_id: int
    renewal_date: date
    previous_expiry_date: date
    new_expiry_date: date
    assigned_to: int | None = None
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")


class RenewalUpdate(BaseModel):
    renewal_date: date | None = None
    previous_expiry_date: date | None = None
    new_expiry_date: date | None = None
    assigned_to: int | None = None
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")


class RenewalStatusUpdate(BaseModel):
    status: RenewalStatus

    model_config = ConfigDict(extra="forbid")


class RenewalComplete(BaseModel):
    new_expiry_date: date | None = None
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")


class RenewalResponse(BaseModel):
    id: int
    contract_id: int
    renewal_date: date
    previous_expiry_date: date
    new_expiry_date: date
    status: RenewalStatus
    assigned_to: int | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UpcomingRenewalResponse(BaseModel):
    contract_id: int
    renewal_id: int | None
    expiry_date: date
    days_remaining: int
    status: RenewalStatus
