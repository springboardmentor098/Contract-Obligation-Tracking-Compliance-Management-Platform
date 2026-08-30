from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    contract_id: UUID | None = None
    obligation_id: UUID | None = None

    notification_type: str
    title: str
    message: str

    scheduled_at: datetime | None = None
    sent_at: datetime | None = None
    read_at: datetime | None = None
    status: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationCreate(BaseModel):
    user_id: UUID
    contract_id: UUID | None = None
    obligation_id: UUID | None = None

    notification_type: str
    title: str
    message: str

    scheduled_at: datetime | None = None
    status: str | None = "Pending"


class NotificationMarkRead(BaseModel):
    read: bool = True