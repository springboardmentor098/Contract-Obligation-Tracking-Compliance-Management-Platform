from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.all_models import NotificationTypeEnum, NotificationStatusEnum

# 1. Base Schema (Shared fields)
class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: NotificationTypeEnum
    contract_id: Optional[int] = None
    obligation_id: Optional[int] = None

# 2. Schema for Creating a Notification
class NotificationCreate(NotificationBase):
    user_id: int

# 3. Schema for Returning Notification Data (Response)
class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    status: NotificationStatusEnum
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True