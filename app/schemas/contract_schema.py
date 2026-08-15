from datetime import date

from pydantic import BaseModel, ConfigDict


class ContractCreate(BaseModel):
    title: str
    contract_number: str | None = None
    description: str | None = None
    party_name: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = None
    owner_id: int


class ContractResponse(BaseModel):
    id: int
    title: str
    contract_number: str | None
    description: str | None
    party_name: str | None
    start_date: date | None
    end_date: date | None
    status: str | None
    owner_id: int

    model_config = ConfigDict(from_attributes=True)