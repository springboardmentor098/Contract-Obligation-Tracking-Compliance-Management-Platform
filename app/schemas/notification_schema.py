from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationCreate(BaseModel):
    user_id: int
    contract_id: Optional[int] = None
    obligation_id: Optional[int] = None
    notification_type: str
    title: str
    message: str
    scheduled_at: Optional[datetime] = None


class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    status: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None


class NotificationStatusUpdate(BaseModel):
    status: str


class NotificationResponse(BaseModel):
    id: int
    user_id: Optional[int]
    contract_id: Optional[int]
    obligation_id: Optional[int]
    notification_type: str
    title: str
    message: str
    status: str
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    read_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True