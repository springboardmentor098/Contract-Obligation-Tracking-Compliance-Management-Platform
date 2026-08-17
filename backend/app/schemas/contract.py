from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ContractCreate(BaseModel):
    title: str
    contract_number: str
    category: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class ContractResponse(BaseModel):
    id: UUID
    title: str
    contract_number: str
    category: str | None
    description: str | None
    start_date: date | None
    end_date: date | None
    status: str | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ContractUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = None