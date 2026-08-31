from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NotificationCreate(BaseModel):
    user_id: int
    contract_id: Optional[int] = None
    obligation_id: Optional[int] = None
    renewal_id: Optional[int] = None
    notification_type: str
    title: str
    message: str


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    contract_id: Optional[int] = None
    obligation_id: Optional[int] = None
    renewal_id: Optional[int] = None
    notification_type: str
    title: str
    message: str
    status: str
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationStatusUpdate(BaseModel):
    status: str