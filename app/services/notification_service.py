from datetime import datetime

from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    contract_id: int | None = None,
    obligation_id: int | None = None
):
    notification = Notification(
        user_id=user_id,
        contract_id=contract_id,
        obligation_id=obligation_id,
        notification_type=notification_type,
        title=title,
        message=message,
        status="Unread"
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def mark_notification_as_read(
    db: Session,
    notification: Notification
):
    notification.status = "Read"
    notification.read_at = datetime.utcnow()

    db.commit()
    db.refresh(notification)

    return notification