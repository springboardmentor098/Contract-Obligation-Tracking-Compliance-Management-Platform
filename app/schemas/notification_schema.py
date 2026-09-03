from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


# ============================================================
# NOTIFICATION TYPES
# ============================================================

NOTIFICATION_TYPES = {
    "Renewal Reminder",
    "Obligation Due Alert",
    "Obligation Overdue Alert",
    "Compliance Alert",
    "Contract Approval Alert",
    "Contract Status Alert",
}


# ============================================================
# NOTIFICATION STATUSES
# ============================================================

NOTIFICATION_STATUSES = {
    "Unread",
    "Read",
}


# ============================================================
# CREATE NOTIFICATION
# ============================================================

class NotificationCreate(BaseModel):

    user_id: int

    contract_id: int | None = None

    obligation_id: int | None = None

    notification_type: str

    title: str

    message: str

    scheduled_at: datetime | None = None

    @field_validator("notification_type")
    @classmethod
    def validate_notification_type(cls, value: str):

        if value not in NOTIFICATION_TYPES:
            raise ValueError(
                f"Invalid notification type. Allowed types: "
                f"{', '.join(sorted(NOTIFICATION_TYPES))}"
            )

        return value


# ============================================================
# UPDATE NOTIFICATION STATUS
# ============================================================

class NotificationStatusUpdate(BaseModel):

    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str):

        if value not in NOTIFICATION_STATUSES:
            raise ValueError(
                f"Invalid notification status. Allowed statuses: "
                f"{', '.join(sorted(NOTIFICATION_STATUSES))}"
            )

        return value


# ============================================================
# NOTIFICATION RESPONSE
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

    model_config = ConfigDict(
        from_attributes=True
    )