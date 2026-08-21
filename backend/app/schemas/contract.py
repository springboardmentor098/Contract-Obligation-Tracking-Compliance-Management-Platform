from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ContractCreate(BaseModel):
    title: str
    contract_number: str
    category: str
    description: str | None = None
    counterparty_name: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    contract_value: Decimal | None = Field(
        default=None,
        max_digits=15,
        decimal_places=2,
    )
    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )
    assigned_to: UUID | None = None


class ContractUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    description: str | None = None
    counterparty_name: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    contract_value: Decimal | None = Field(
        default=None,
        max_digits=15,
        decimal_places=2,
    )
    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
    )
    assigned_to: UUID | None = None


class ContractStatusUpdate(BaseModel):
    status: str


class ContractAssignment(BaseModel):
    assigned_to: UUID


class ContractResponse(BaseModel):
    id: UUID
    title: str
    contract_number: str
    category: str | None
    description: str | None
    counterparty_name: str | None
    start_date: date | None
    end_date: date | None
    contract_value: Decimal | None
    currency: str | None
    status: str
    created_by: UUID
    assigned_to: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)