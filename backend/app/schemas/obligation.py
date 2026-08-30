from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ObligationCreate(BaseModel):
    contract_id: UUID
    assigned_to: UUID
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    obligation_type: str | None = Field(default=None, max_length=100)
    due_date: date | None = None
    status: str | None = Field(default="Pending", max_length=50)
    priority: str | None = Field(default="Medium", max_length=20)


class ObligationUpdate(BaseModel):
    assigned_to: UUID | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    obligation_type: str | None = Field(default=None, max_length=100)
    due_date: date | None = None
    priority: str | None = Field(default=None, max_length=20)


class ObligationStatusUpdate(BaseModel):
    status: str = Field(..., min_length=1, max_length=50)


class ObligationResponse(BaseModel):
    id: UUID
    contract_id: UUID
    assigned_to: UUID
    title: str
    description: str | None
    obligation_type: str | None
    due_date: date | None
    status: str | None
    priority: str | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)