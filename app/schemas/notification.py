# app/schemas/notification.py

from datetime import datetime

from pydantic import BaseModel, ConfigDict


# =========================================================
# CREATE NOTIFICATION
# =========================================================

class NotificationCreate(BaseModel):

    user_id: int

    contract_id: int | None = None

    obligation_id: int | None = None

    notification_type: str

    title: str

    message: str

    scheduled_at: datetime | None = None


# =========================================================
# NOTIFICATION RESPONSE
# =========================================================

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

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# MARK AS READ RESPONSE
# =========================================================

class NotificationReadResponse(BaseModel):

    id: int

    status: str

    read_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )