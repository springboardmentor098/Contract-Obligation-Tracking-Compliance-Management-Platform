from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ObligationBase(BaseModel):
    title: str
    description: str | None = None
    obligation_type: str
    due_date: date
    assigned_to: int


class ObligationCreate(ObligationBase):
    contract_id: int


class ObligationUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    obligation_type: str | None = None
    due_date: date | None = None
    assigned_to: int | None = None


class ObligationStatusUpdate(BaseModel):
    status: str


class ObligationResponse(ObligationBase):
    id: int
    contract_id: int
    status: str
    completion_date: date | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)