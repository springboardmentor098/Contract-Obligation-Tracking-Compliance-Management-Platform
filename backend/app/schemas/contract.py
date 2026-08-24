from datetime import date, datetime
from pydantic import BaseModel


# CREATE CONTRACT
class ContractCreate(BaseModel):
    title: str
    contract_number: str
    category: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None


# UPDATE CONTRACT
class ContractUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None


# UPDATE CONTRACT STATUS
class ContractStatusUpdate(BaseModel):
    status: str


# ASSIGN CONTRACT
class ContractAssignment(BaseModel):
    assigned_to: int


# CONTRACT RESPONSE
class ContractOut(BaseModel):
    id: int
    owner_id: int
    contract_number: str
    title: str
    category: str
    description: str | None
    start_date: date | None
    end_date: date | None
    status: str
    assigned_to: int | None
    reviewed_at: datetime | None
    approved_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True