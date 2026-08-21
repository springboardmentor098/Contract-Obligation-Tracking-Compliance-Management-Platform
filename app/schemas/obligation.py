from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ObligationCreate(BaseModel):
    contract_id: int
    title: str
    description: str | None = None
    obligation_type: str
    due_date: date
    assigned_to: int


class ObligationUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    obligation_type: str | None = None
    due_date: date | None = None


class ObligationAssignment(BaseModel):
    assigned_to: int


class ObligationStatusUpdate(BaseModel):
    status: str


class ObligationProgressUpdate(BaseModel):
    progress: int


class ObligationResponse(BaseModel):
    id: int
    contract_id: int
    title: str
    description: str | None
    obligation_type: str
    due_date: date
    status: str
    progress: int
    assigned_to: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )