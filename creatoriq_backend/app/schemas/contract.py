from datetime import date
from pydantic import BaseModel, Field


class ContractCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    contract_number: str = Field(..., min_length=1, max_length=100)
    category: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class ContractResponse(BaseModel):
    id: int
    title: str
    contract_number: str
    category: str
    description: str | None
    start_date: date | None
    end_date: date | None
    status: str
    created_by: int
    assigned_to: int

    class Config:
        from_attributes = True


class ContractUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = None
    assigned_to: int | None = None