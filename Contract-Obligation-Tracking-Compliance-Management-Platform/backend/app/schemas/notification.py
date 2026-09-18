from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


ALLOWED_NOTIFICATION_TYPES = {
    "Renewal Reminder",
    "Obligation Due Alert",
    "Obligation Overdue Alert",
    "Compliance Alert",
    "Contract Approval Alert",
    "Contract Status Alert",
}


class NotificationCreate(BaseModel):
    user_id: int = Field(..., gt=0)

    contract_id: int | None = Field(
        default=None,
        gt=0,
    )

    obligation_id: int | None = Field(
        default=None,
        gt=0,
    )

    notification_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    message: str = Field(
        ...,
        min_length=1,
    )

    scheduled_at: datetime | None = None


class NotificationResponse(BaseModel):
    id: int
    user_id: int

    contract_id: int | None = None
    obligation_id: int | None = None

    notification_type: str
    title: str
    message: str

    status: str

    scheduled_at: datetime | None = None
    sent_at: datetime | None = None
    read_at: datetime | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class NotificationReadResponse(BaseModel):
    id: int
    status: str
    read_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class MarkAllReadResponse(BaseModel):
    message: str
    updated_count: int