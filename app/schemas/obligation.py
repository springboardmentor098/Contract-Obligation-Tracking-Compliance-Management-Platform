from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


VALID_OBLIGATION_TYPES = [
    "Payment Obligation",
    "Delivery Commitment",
    "Reporting Requirement",
    "Renewal Condition",
    "Service Level Agreement",
    "Legal Compliance Requirement",
]

VALID_OBLIGATION_STATUSES = [
    "Pending",
    "In Progress",
    "Completed",
    "Delayed",
    "Overdue",
]


class ObligationCreate(BaseModel):
    contract_id: int = Field(..., description="ID of associated contract", example=1)
    title: str = Field(..., description="Name of obligation", example="Submit Monthly Service Report")
    description: Optional[str] = Field(None, description="Detailed description", example="Vendor must submit the monthly service report.")
    obligation_type: str = Field(..., description="Type of obligation", example="Reporting Requirement")
    due_date: Optional[date] = Field(None, description="Deadline date", example="2026-08-30")
    assigned_to: int = Field(..., description="ID of responsible user", example=5)


class ObligationUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Updated name of obligation")
    description: Optional[str] = Field(None, description="Updated description")
    obligation_type: Optional[str] = Field(None, description="Updated type")
    due_date: Optional[date] = Field(None, description="Updated due date")
    assigned_to: Optional[int] = Field(None, description="Updated responsible user ID")


class ObligationStatusUpdate(BaseModel):
    status: str = Field(..., description="Target status (e.g. In Progress, Completed)", example="In Progress")


class ObligationResponse(BaseModel):
    id: int
    contract_id: int
    title: str
    description: Optional[str] = None
    obligation_type: str
    due_date: Optional[date] = None
    assigned_to: int
    status: str
    completion_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
