from datetime import datetime
from typing import Literal

from pydantic import BaseModel


NotificationType = Literal[
    "Renewal Reminder",
    "Obligation Due Alert",
    "Obligation Overdue Alert",
    "Compliance Alert",
    "Contract Approval Alert",
    "Contract Status Alert"
]


NotificationStatus = Literal[
    "Unread",
    "Read"
]


class NotificationCreate(BaseModel):
    user_id: int
    contract_id: int | None = None
    obligation_id: int | None = None
    notification_type: NotificationType
    title: str
    message: str


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    contract_id: int | None
    obligation_id: int | None
    notification_type: NotificationType
    title: str
    message: str
    status: NotificationStatus
    scheduled_at: datetime | None
    sent_at: datetime | None
    read_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationStatusUpdate(BaseModel):
    status: NotificationStatus