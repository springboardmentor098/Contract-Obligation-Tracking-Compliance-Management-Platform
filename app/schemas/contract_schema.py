from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ContractBase(BaseModel):
    contract_number: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    counterparty_name: str = Field(..., min_length=1, max_length=255)
    start_date: date
    end_date: date | None = None


class ContractCreate(ContractBase):
    assigned_to: int | None = None


class ContractUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    category: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    counterparty_name: str | None = Field(None, min_length=1, max_length=255)
    start_date: date | None = None
    end_date: date | None = None
    assigned_to: int | None = None


class ContractRead(ContractBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by: int
    assigned_to: int | None
    status: str
    reviewed_at: datetime | None
    approved_at: datetime | None
    created_at: datetime
    updated_at: datetime