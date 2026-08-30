from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# CREATE NOTIFICATION
# ============================================================
class NotificationCreate(BaseModel):
    user_id: int
    contract_id: Optional[int] = None
    obligation_id: Optional[int] = None

    notification_type: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=255
    )

    message: str = Field(
        ...,
        min_length=1
    )

    scheduled_at: Optional[datetime] = None


# ============================================================
# UPDATE NOTIFICATION STATUS
# ============================================================
class NotificationStatusUpdate(BaseModel):
    status: str


# ============================================================
# NOTIFICATION RESPONSE
# ============================================================
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

    model_config = ConfigDict(
        from_attributes=True
    )