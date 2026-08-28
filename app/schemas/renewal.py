from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


VALID_RENEWAL_STATUSES = ["Upcoming", "In Progress", "Renewed", "Expired", "Cancelled"]

# Valid Lifecycle Transitions
# Upcoming -> In Progress, Expired, Cancelled
# In Progress -> Renewed, Cancelled
VALID_STATUS_TRANSITIONS = {
    "Upcoming": ["In Progress", "Expired", "Cancelled"],
    "In Progress": ["Renewed", "Cancelled"],
    "Renewed": [],
    "Expired": [],
    "Cancelled": [],
}


class RenewalBase(BaseModel):
    renewal_date: Optional[date] = None
    previous_expiry_date: Optional[date] = None
    new_expiry_date: Optional[date] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None
    status: Optional[str] = "Upcoming"


class RenewalCreate(BaseModel):
    contract_id: int = Field(1, description="ID of associated contract")
    renewal_date: Optional[date] = None
    previous_expiry_date: Optional[date] = None
    new_expiry_date: Optional[date] = None
    assigned_to: Optional[int] = Field(None, description="Assigned user ID")
    notes: Optional[str] = None
    status: Optional[str] = "Upcoming"



class RenewalUpdate(BaseModel):
    renewal_date: Optional[date] = None
    previous_expiry_date: Optional[date] = None
    new_expiry_date: Optional[date] = None
    assigned_to: Optional[int] = None
    notes: Optional[str] = None


class RenewalStatusUpdate(BaseModel):
    status: str = Field(..., description="New renewal status")


class RenewalComplete(BaseModel):
    new_expiry_date: Optional[date] = None
    notes: Optional[str] = None


class RenewalResponse(BaseModel):
    id: int
    contract_id: int
    renewal_date: Optional[date] = None
    previous_expiry_date: Optional[date] = None
    new_expiry_date: Optional[date] = None
    status: str
    assigned_to: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UpcomingRenewalResponse(BaseModel):
    contract_id: int
    title: str
    contract_number: str
    end_date: date
    days_remaining: int
    status: str


class ExpiredContractResponse(BaseModel):
    contract_id: int
    title: str
    contract_number: str
    end_date: date
    days_expired: int
    status: str
