# app/schemas/contract.py

from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class ContractCreate(BaseModel):
    title: str
    contract_number: str
    category: str
    description: str | None = None
    start_date: date
    end_date: date | None = None
    status: str
    owner_id: int


class ContractResponse(BaseModel):
    id: int
    title: str
    contract_number: str
    category: str
    description: str | None
    start_date: date
    end_date: date | None
    status: str
    owner_id: int
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
