from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(
    db: Session,
    user_id: UUID,
    notification_type: str,
    title: str,
    message: str,
    contract_id: UUID | None = None,
    obligation_id: UUID | None = None,
    scheduled_at: datetime | None = None,
    status: str = "Pending",
) -> Notification:
    """
    Create and persist a notification for a user.
    """

    notification = Notification(
        user_id=user_id,
        contract_id=contract_id,
        obligation_id=obligation_id,
        notification_type=notification_type,
        title=title,
        message=message,
        scheduled_at=scheduled_at,
        status=status,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def get_notification(
    db: Session,
    notification_id: UUID,
    user_id: UUID | None = None,
) -> Notification | None:
    """
    Get a single notification.

    If user_id is provided, only that user's notification
    can be returned.
    """

    query = select(Notification).where(
        Notification.id == notification_id
    )

    if user_id is not None:
        query = query.where(
            Notification.user_id == user_id
        )

    return db.execute(query).scalar_one_or_none()


def get_user_notifications(
    db: Session,
    user_id: UUID,
) -> list[Notification]:
    """
    Return all notifications belonging to a user,
    newest first.
    """

    return db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
    ).scalars().all()


def get_unread_notifications(
    db: Session,
    user_id: UUID,
) -> list[Notification]:
    """
    Return unread notifications for a user.
    """

    return db.execute(
        select(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.read_at.is_(None),
        )
        .order_by(Notification.created_at.desc())
    ).scalars().all()


def mark_notification_as_read(
    db: Session,
    notification: Notification,
) -> Notification:
    """
    Mark a notification as read.
    """

    notification.read_at = datetime.utcnow()

    db.commit()
    db.refresh(notification)

    return notification


def mark_notification_as_unread(
    db: Session,
    notification: Notification,
) -> Notification:
    """
    Mark a notification as unread.
    """

    notification.read_at = None

    db.commit()
    db.refresh(notification)

    return notification


def mark_all_notifications_as_read(
    db: Session,
    user_id: UUID,
) -> int:
    """
    Mark all unread notifications belonging to a user as read.

    Returns the number of notifications updated.
    """

    notifications = db.execute(
        select(Notification).where(
            Notification.user_id == user_id,
            Notification.read_at.is_(None),
        )
    ).scalars().all()

    now = datetime.utcnow()

    for notification in notifications:
        notification.read_at = now

    db.commit()

    return len(notifications)


def delete_notification(
    db: Session,
    notification: Notification,
) -> None:
    """
    Delete a notification.
    """

    db.delete(notification)
    db.commit()