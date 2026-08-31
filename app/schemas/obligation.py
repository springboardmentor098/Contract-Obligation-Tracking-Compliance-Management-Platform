from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ObligationBase(BaseModel):
    description: str
    due_date: date
    status: Optional[str] = "pending"
    responsible_party: Optional[str] = None


class ObligationCreate(ObligationBase):
    contract_id: int


class ObligationResponse(ObligationBase):
    id: int
    contract_id: int
    created_at: datetime

    class Config:
        from_attributes = True
