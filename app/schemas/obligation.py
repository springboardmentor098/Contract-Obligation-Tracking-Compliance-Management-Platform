from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from app.models.all_models import ObligationType, ObligationStatus

# 1. Base Schema (Shared fields)
class ObligationBase(BaseModel):
    title: str
    description: Optional[str] = None
    obligation_type: ObligationType
    due_date: date
    assigned_to: int

# 2. Schema for Creating an Obligation (Requires contract_id)
class ObligationCreate(ObligationBase):
    contract_id: int

# 3. Schema for Updating Details (All fields are optional)
class ObligationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    obligation_type: Optional[ObligationType] = None
    due_date: Optional[date] = None
    assigned_to: Optional[int] = None

# 4. Schema for Manually Updating Status
class ObligationStatusUpdate(BaseModel):
    status: ObligationStatus

# 5. Schema for Returning Obligation Data (Response)
class ObligationResponse(ObligationBase):
    id: int
    contract_id: int
    status: ObligationStatus
    completion_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True