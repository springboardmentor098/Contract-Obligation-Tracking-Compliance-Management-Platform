from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# 1. Create Notification
# ============================================================

class NotificationCreate(BaseModel):
    user_id: int
    contract_id: int | None = None
    obligation_id: int | None = None
    notification_type: str
    title: str
    message: str
    scheduled_at: datetime | None = None


# ============================================================
# 2. Notification Response
# ============================================================

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

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 3. Notification List Response
# ============================================================

class NotificationListResponse(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)