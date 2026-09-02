from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from app.models.all_models import RenewalStatus

# 1. Base Schema (Shared fields)
class RenewalBase(BaseModel):
    renewal_date: date
    previous_expiry_date: date
    new_expiry_date: date
    assigned_to: int
    notes: Optional[str] = None

# 2. Schema for Creating a Renewal
class RenewalCreate(RenewalBase):
    contract_id: int

# 3. Schema for Updating Details (All fields are optional)
class RenewalUpdate(BaseModel):
    renewal_date: Optional[date] = None
    previous_expiry_date: Optional[date] = None
    new_expiry_date: Optional[date] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None

# 4. Schema for Manually Updating Status
class RenewalStatusUpdate(BaseModel):
    status: RenewalStatus

# 5. Schema for Returning Renewal Data (Response)
class RenewalResponse(RenewalBase):
    id: int
    contract_id: int
    status: RenewalStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True