from datetime import datetime

from sqlalchemy.orm import Session

from app.models.notification import Notification


ALLOWED_NOTIFICATION_TYPES = {
    "Renewal Reminder",
    "Obligation Due Alert",
    "Obligation Overdue Alert",
    "Compliance Alert",
    "Contract Approval Alert",
    "Contract Status Alert",
}


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: str,
    contract_id: int | None = None,
    obligation_id: int | None = None,
    renewal_id: int | None = None,
    scheduled_at: datetime | None = None,
):
    if notification_type not in ALLOWED_NOTIFICATION_TYPES:
        raise ValueError("Invalid notification type")

    notification = Notification(
        user_id=user_id,
        contract_id=contract_id,
        obligation_id=obligation_id,
        renewal_id=renewal_id,
        notification_type=notification_type,
        title=title,
        message=message,
        status="Unread",
        scheduled_at=scheduled_at,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification