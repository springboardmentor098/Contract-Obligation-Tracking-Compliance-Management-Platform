from datetime import date, datetime

from pydantic import BaseModel


# Schema used when creating a contract
class ContractCreate(BaseModel):
    title: str
    contract_number: str
    category: str
    description: str | None = None
    start_date: date
    end_date: date | None = None


# Schema used when updating a contract
class ContractUpdate(BaseModel):
    title: str
    contract_number: str
    category: str
    description: str | None = None
    start_date: date
    end_date: date | None = None
    status: str


# Schema returned by the API
class ContractResponse(BaseModel):
    id: int
    title: str
    contract_number: str
    category: str
    description: str | None
    start_date: date
    end_date: date | None
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True