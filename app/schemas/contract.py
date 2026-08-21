from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ContractCreate(BaseModel):
    title: str
    contract_number: str
    category: str
    description: str | None = None
    start_date: date
    end_date: date


class ContractUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class ContractStatusUpdate(BaseModel):
    status: str


class ContractAssignment(BaseModel):
    assigned_to: int


class ContractResponse(BaseModel):
    id: int
    title: str
    contract_number: str
    category: str
    description: str | None
    start_date: date
    end_date: date
    status: str
    created_by: int
    assigned_to: int | None
    created_at: datetime
    updated_at: datetime
    reviewed_at: datetime | None
    approved_at: datetime | None

    model_config = ConfigDict(from_attributes=True)