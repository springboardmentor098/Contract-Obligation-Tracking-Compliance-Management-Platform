# app/schemas/notification.py

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotificationCreate(BaseModel):
    user_id: int
    contract_id: int | None = None
    obligation_id: int | None = None
    notification_type: str
    message: str
    channel: str
    is_read: bool = False
    sent_at: datetime | None = None


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    contract_id: int | None
    obligation_id: int | None
    notification_type: str
    message: str
    channel: str
    is_read: bool
    sent_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
