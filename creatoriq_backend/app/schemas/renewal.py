from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator


# ============================================================
# 1. Create Renewal
# ============================================================

class RenewalCreate(BaseModel):
    contract_id: int
    renewal_date: date
    previous_expiry_date: date
    new_expiry_date: date
    assigned_to: int
    notes: str | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.new_expiry_date < self.renewal_date:
            raise ValueError(
                "New expiry date cannot be earlier than renewal date"
            )

        return self


# ============================================================
# 2. Update Renewal
# ============================================================

class RenewalUpdate(BaseModel):
    renewal_date: date | None = None
    new_expiry_date: date | None = None
    assigned_to: int | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.renewal_date is not None
            and self.new_expiry_date is not None
            and self.new_expiry_date < self.renewal_date
        ):
            raise ValueError(
                "New expiry date cannot be earlier than renewal date"
            )

        return self


# ============================================================
# 3. Update Renewal Status
# ============================================================

class RenewalStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        description="Upcoming, In Progress, Renewed, Expired, or Cancelled"
    )


# ============================================================
# 4. Complete Renewal
# ============================================================

class RenewalComplete(BaseModel):
    new_expiry_date: date


# ============================================================
# 5. Renewal Response
# ============================================================

class RenewalResponse(BaseModel):
    id: int
    contract_id: int
    renewal_date: date
    previous_expiry_date: date
    new_expiry_date: date
    status: str
    assigned_to: int
    approval_status: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True