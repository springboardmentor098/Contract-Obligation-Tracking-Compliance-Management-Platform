# app/schemas/obligation.py

from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class ObligationCreate(BaseModel):
    contract_id: int
    title: str
    description: str | None = None
    obligation_type: str
    due_date: date
    assigned_to: int
    status: str
    compliance_status: str
    completed_at: datetime | None = None


class ObligationResponse(BaseModel):
    id: int
    contract_id: int
    title: str
    description: str | None
    obligation_type: str
    due_date: date
    assigned_to: int
    status: str
    compliance_status: str
    completed_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)