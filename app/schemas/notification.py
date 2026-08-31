from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


VALID_NOTIFICATION_TYPES = [
    "Renewal Reminder",
    "Obligation Due Alert",
    "Obligation Overdue Alert",
    "Compliance Alert",
    "Contract Approval Alert",
    "Contract Status Alert",
]


class NotificationCreate(BaseModel):
    user_id: Optional[int] = Field(0, description="ID of recipient user (defaults to authenticated user if 0 or omitted)")
    contract_id: Optional[int] = Field(None, description="Related contract ID")
    obligation_id: Optional[int] = Field(None, description="Related obligation ID")
    notification_type: str = Field("Renewal Reminder", description="Type of notification")
    title: str = Field("Contract Renewal Approaching", description="Notification title")
    message: str = Field("ABC Vendor Agreement expires in 30 days.", description="Notification body")


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    contract_id: Optional[int] = None
    obligation_id: Optional[int] = None
    notification_type: str
    title: str
    message: str
    status: str
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationReadResponse(BaseModel):
    id: int
    status: str
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReadAllResponse(BaseModel):
    message: str
    updated_count: int
