# app/schemas/renewal.py

from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional


# =========================================================
# CREATE RENEWAL
# =========================================================

class RenewalCreate(BaseModel):
    contract_id: int

    renewal_date: date

    previous_expiry_date: date

    new_expiry_date: Optional[date] = None

    assigned_to: Optional[int] = None

    notes: Optional[str] = None

    @field_validator("new_expiry_date")
    @classmethod
    def validate_new_expiry_date(cls, value, info):
        renewal_date = info.data.get("renewal_date")

        if value is not None and renewal_date is not None:
            if value < renewal_date:
                raise ValueError(
                    "New expiry date cannot be earlier than renewal date"
                )

        return value


# =========================================================
# UPDATE RENEWAL
# =========================================================

class RenewalUpdate(BaseModel):

    renewal_date: Optional[date] = None

    new_expiry_date: Optional[date] = None

    assigned_to: Optional[int] = None

    notes: Optional[str] = None


# =========================================================
# UPDATE RENEWAL STATUS
# =========================================================

class RenewalStatusUpdate(BaseModel):

    status: str


# =========================================================
# RENEWAL RESPONSE
# =========================================================

class RenewalResponse(BaseModel):

    id: int

    contract_id: int

    renewal_date: date

    previous_expiry_date: date

    new_expiry_date: Optional[date]

    status: str

    assigned_to: Optional[int]

    notes: Optional[str]

    created_at: datetime

    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)