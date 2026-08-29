from datetime import datetime

from pydantic import BaseModel


class NotificationCreate(BaseModel):
    user_id: int
    contract_id: int | None = None
    obligation_id: int | None = None
    notification_type: str
    title: str
    message: str


class NotificationStatusUpdate(BaseModel):
    status: str


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    contract_id: int | None
    obligation_id: int | None
    notification_type: str
    title: str
    message: str
    status: str
    scheduled_at: datetime | None
    sent_at: datetime | None
    read_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True