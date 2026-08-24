from datetime import date, datetime

from pydantic import BaseModel


# CREATE OBLIGATION
class ObligationCreate(BaseModel):
    contract_id: int
    title: str
    description: str | None = None
    obligation_type: str
    due_date: date
    assigned_to: int


# UPDATE OBLIGATION
class ObligationUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    obligation_type: str | None = None
    due_date: date | None = None
    assigned_to: int | None = None


# UPDATE OBLIGATION STATUS
class ObligationStatusUpdate(BaseModel):
    status: str


# OBLIGATION RESPONSE
class ObligationOut(BaseModel):
    id: int
    contract_id: int
    title: str
    description: str | None
    obligation_type: str
    due_date: date
    assigned_to: int
    status: str
    completion_date: date | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True