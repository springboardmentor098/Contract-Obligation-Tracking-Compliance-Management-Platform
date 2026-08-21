from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ObligationCreate(BaseModel):
    contract_id: int
    title: str
    description: Optional[str] = None
    obligation_type: str
    due_date: date
    assigned_to: int


class ObligationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    obligation_type: Optional[str] = None
    due_date: Optional[date] = None
    assigned_to: Optional[int] = None


class ObligationStatusUpdate(BaseModel):
    status: str


class ObligationResponse(BaseModel):
    id: int
    contract_id: int
    title: str
    description: Optional[str] = None
    obligation_type: str
    due_date: date
    assigned_to: int
    status: str
    completion_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)