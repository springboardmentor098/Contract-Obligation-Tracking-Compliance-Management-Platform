from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ContractCreate(BaseModel):
    title: str
    contract_code: str
    category: str
    description: str | None = None
    counterparty: str
    risk_level: str = "Medium"
    start_date: date
    end_date: date


class ContractUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    description: str | None = None
    counterparty: str | None = None
    risk_level: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = None


class ContractResponse(BaseModel):
    id: int
    owner_id: int
    contract_code: str
    title: str
    description: str | None
    counterparty: str
    category: str
    status: str
    risk_level: str
    start_date: date
    end_date: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)