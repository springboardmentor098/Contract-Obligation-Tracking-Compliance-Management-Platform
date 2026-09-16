from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotificationCreate(BaseModel):
    user_id: int
    contract_id: int | None = None

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    message: str = Field(
        ...,
        min_length=1,
    )

    notification_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )


class NotificationUpdate(BaseModel):
    is_read: bool


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    contract_id: int | None
    title: str
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime
