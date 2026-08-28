# app/services/notification_service.py

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.notification import Notification


# =========================================================
# SUPPORTED NOTIFICATION TYPES
# =========================================================

NOTIFICATION_TYPES = {
    "Renewal Reminder",
    "Obligation Due Alert",
    "Obligation Overdue Alert",
    "Compliance Alert",
    "Contract Approval Alert",
    "Contract Status Alert",
}


# =========================================================
# CREATE NOTIFICATION
# =========================================================

def create_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    contract_id: int | None = None,
    obligation_id: int | None = None,
    scheduled_at: datetime | None = None,
):
    """
    Create a new notification.

    Every new notification starts with:
        status = "Unread"
    """

    # -----------------------------------------------------
    # Validate notification type
    # -----------------------------------------------------

    if notification_type not in NOTIFICATION_TYPES:
        raise ValueError(
            f"Invalid notification type: {notification_type}"
        )

    # -----------------------------------------------------
    # Create notification
    # -----------------------------------------------------

    notification = Notification(
        user_id=user_id,
        contract_id=contract_id,
        obligation_id=obligation_id,
        notification_type=notification_type,
        title=title,
        message=message,
        status="Unread",
        scheduled_at=scheduled_at,
    )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    db.add(notification)

    db.commit()

    db.refresh(notification)

    return notification