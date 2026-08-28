from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


# Used when creating a new obligation
class ObligationCreate(BaseModel):
    contract_id: int
    title: str
    description: str | None = None
    obligation_type: str
    due_date: date
    assigned_to: int


# Used when updating obligation details
class ObligationUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    obligation_type: str | None = None
    due_date: date | None = None
    assigned_to: int | None = None


# Used when changing obligation status
class ObligationStatusUpdate(BaseModel):
    status: str


# Used when completing an obligation
class ObligationComplete(BaseModel):
    pass


# Returned to the client
class ObligationResponse(BaseModel):
    id: int
    contract_id: int
    title: str
    description: str | None
    obligation_type: str
    due_date: date
    assigned_to: int
    status: str
    progress: int | None
    completion_date: date | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)