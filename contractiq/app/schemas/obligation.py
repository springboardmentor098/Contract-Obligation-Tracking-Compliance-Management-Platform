from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.obligation import ObligationType, ObligationStatus


class ObligationCreate(BaseModel):
    contract_id: int
    title: str
    description: Optional[str] = None
    obligation_type: ObligationType
    due_date: date
    assigned_to: Optional[int] = None


class ObligationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    obligation_type: Optional[ObligationType] = None
    due_date: Optional[date] = None
    assigned_to: Optional[int] = None


class ObligationStatusUpdate(BaseModel):
    status: ObligationStatus


class ObligationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contract_id: int
    title: str
    description: Optional[str] = None
    obligation_type: ObligationType
    due_date: date
    assigned_to: Optional[int] = None
    status: ObligationStatus
    completion_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime


class ObligationListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contract_id: int
    title: str
    obligation_type: ObligationType
    due_date: date
    status: ObligationStatus
