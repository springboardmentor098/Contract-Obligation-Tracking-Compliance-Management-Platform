from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


# Contract Categories supported by ContractIQ
VALID_CONTRACT_CATEGORIES = [
    "Employment Contract",
    "Vendor Contract",
    "Service Agreement",
    "Lease Agreement",
    "Purchase Agreement",
    "Partnership Agreement",
    "Confidentiality Agreement",
]

# Contract Statuses supported by ContractIQ
VALID_CONTRACT_STATUSES = [
    "Draft",
    "Under Review",
    "Approved",
    "Active",
    "Expired",
    "Terminated",
]


class ContractCreate(BaseModel):
    title: str = Field(..., description="Title of the contract", example="ABC Vendor Agreement")
    contract_number: str = Field(..., description="Unique business reference number", example="CNT-1001")
    category: str = Field(..., description="Category / type of contract", example="Vendor Contract")
    description: Optional[str] = Field(None, description="Detailed contract description", example="Annual vendor service agreement")
    start_date: Optional[date] = Field(None, description="Contract start date", example="2026-08-01")
    end_date: Optional[date] = Field(None, description="Contract expiry date", example="2027-07-31")
    status: Optional[str] = Field("Draft", description="Current contract status", example="Draft")


class ContractUpdate(BaseModel):
    title: Optional[str] = None
    contract_number: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None


class ContractResponse(BaseModel):
    id: int
    title: str
    contract_number: str
    category: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
