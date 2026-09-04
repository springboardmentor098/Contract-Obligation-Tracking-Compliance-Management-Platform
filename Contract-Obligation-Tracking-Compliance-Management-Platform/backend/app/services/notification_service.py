from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.schemas.notification import (
    NotificationCreate,
    ALLOWED_NOTIFICATION_TYPES,
)


def create_notification(
    db: Session,
    data: NotificationCreate,
) -> Notification:

    if data.notification_type not in ALLOWED_NOTIFICATION_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid notification type. "
                f"Allowed types: "
                f"{', '.join(sorted(ALLOWED_NOTIFICATION_TYPES))}"
            ),
        )

    notification = Notification(
        user_id=data.user_id,
        contract_id=data.contract_id,
        obligation_id=data.obligation_id,
        notification_type=data.notification_type,
        title=data.title,
        message=data.message,
        status="Unread",
        scheduled_at=data.scheduled_at,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def mark_notification_as_read(
    db: Session,
    notification: Notification,
) -> Notification:

    notification.status = "Read"
    notification.read_at = datetime.now(timezone.utc)
    notification.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(notification)

    return notification


def mark_all_notifications_as_read(
    db: Session,
    user_id: int,
) -> int:

    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.status == "Unread",
        )
        .all()
    )

    now = datetime.now(timezone.utc)

    for notification in notifications:
        notification.status = "Read"
        notification.read_at = now
        notification.updated_at = now

    db.commit()

    return len(notifications)


def generate_renewal_reminder(
    db: Session,
    user_id: int,
    contract_id: int,
    title: str,
    message: str,
) -> Notification:

    data = NotificationCreate(
        user_id=user_id,
        contract_id=contract_id,
        notification_type="Renewal Reminder",
        title=title,
        message=message,
    )

    return create_notification(db, data)


def generate_obligation_due_alert(
    db: Session,
    user_id: int,
    contract_id: int | None,
    obligation_id: int,
    title: str,
    message: str,
) -> Notification:

    data = NotificationCreate(
        user_id=user_id,
        contract_id=contract_id,
        obligation_id=obligation_id,
        notification_type="Obligation Due Alert",
        title=title,
        message=message,
    )

    return create_notification(db, data)


def generate_obligation_overdue_alert(
    db: Session,
    user_id: int,
    contract_id: int | None,
    obligation_id: int,
    title: str,
    message: str,
) -> Notification:

    data = NotificationCreate(
        user_id=user_id,
        contract_id=contract_id,
        obligation_id=obligation_id,
        notification_type="Obligation Overdue Alert",
        title=title,
        message=message,
    )

    return create_notification(db, data)


def generate_compliance_alert(
    db: Session,
    user_id: int,
    contract_id: int,
    title: str,
    message: str,
) -> Notification:

    data = NotificationCreate(
        user_id=user_id,
        contract_id=contract_id,
        notification_type="Compliance Alert",
        title=title,
        message=message,
    )

    return create_notification(db, data)


def generate_approval_notification(
    db: Session,
    user_id: int,
    contract_id: int,
    title: str,
    message: str,
) -> Notification:

    data = NotificationCreate(
        user_id=user_id,
        contract_id=contract_id,
        notification_type="Contract Approval Alert",
        title=title,
        message=message,
    )

    return create_notification(db, data)