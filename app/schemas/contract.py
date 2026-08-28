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
    assigned_to: Optional[int] = Field(None, description="ID of responsible user assigned to contract", example=1)


class ContractUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Title of contract", example="ABC Vendor Agreement - Updated")
    category: Optional[str] = Field(None, description="Category of contract", example="Service Agreement")
    description: Optional[str] = Field(None, description="Description of contract", example="Updated vendor agreement terms")
    start_date: Optional[date] = Field(None, description="Start date of contract", example="2026-08-01")
    end_date: Optional[date] = Field(None, description="End date of contract", example="2027-07-31")
    assigned_to: Optional[int] = Field(None, description="Assigned responsible user ID", example=1)


class ContractStatusUpdate(BaseModel):
    status: str = Field(..., description="New target contract status", example="Under Review")


class ContractAssign(BaseModel):
    assigned_to: int = Field(..., description="User ID to assign to the contract", example=5)


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
    assigned_to: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
