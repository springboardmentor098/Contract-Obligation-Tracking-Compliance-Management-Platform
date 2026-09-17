from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.notification import Notification


# =========================================================
# GET ALL NOTIFICATIONS
# =========================================================

def get_notifications(
    db: Session,
    user_id: int,
):
    """
    Return only notifications belonging to the
    authenticated user.
    """
    return (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id
        )
        .order_by(
            Notification.created_at.desc()
        )
        .all()
    )


# =========================================================
# GET ONE NOTIFICATION
# =========================================================

def get_notification(
    db: Session,
    notification_id: int,
    user_id: int,
):
    """
    Return one notification only when it belongs
    to the authenticated user.
    """
    return (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        .first()
    )


# =========================================================
# CREATE NOTIFICATION
# =========================================================

def create_notification(
    db: Session,
    user_id: int,
    contract_id: Optional[int] = None,
    obligation_id: Optional[int] = None,
    notification_type: str = "",
    title: str = "",
    message: str = "",
    status: Optional[str] = "Unread",
    scheduled_at: Optional[datetime] = None,
):
    """
    Create a notification.

    Timestamp behavior:
      scheduled_at -> optional scheduled time
      sent_at      -> NULL until notification is sent
      read_at      -> NULL until notification is read
      created_at   -> creation timestamp
      updated_at   -> creation/update timestamp
    """

    now = datetime.utcnow()

    notification = Notification(
        user_id=user_id,
        contract_id=contract_id,
        obligation_id=obligation_id,
        notification_type=notification_type,
        title=title,
        message=message,
        status=status or "Unread",

        # Optional scheduled time
        scheduled_at=scheduled_at,

        # New notification has not been sent
        sent_at=None,

        # New notification has not been read
        read_at=None,

        # Always set timestamps explicitly
        created_at=now,
        updated_at=now,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


# =========================================================
# MARK NOTIFICATION AS READ
# =========================================================

def mark_notification_as_read(
    db: Session,
    notification_id: int,
    user_id: int,
):
    """
    Mark one notification as Read.
    Only the owner can update it.
    """

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        .first()
    )

    if notification is None:
        return None

    now = datetime.utcnow()

    notification.status = "Read"
    notification.read_at = now
    notification.updated_at = now

    db.commit()
    db.refresh(notification)

    return notification


# =========================================================
# MARK ALL NOTIFICATIONS AS READ
# =========================================================

def mark_all_notifications_as_read(
    db: Session,
    user_id: int,
):
    """
    Mark all unread notifications belonging to
    the authenticated user as Read.
    """

    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.status != "Read",
        )
        .all()
    )

    now = datetime.utcnow()

    for notification in notifications:

        notification.status = "Read"

        if notification.read_at is None:
            notification.read_at = now

        notification.updated_at = now

    db.commit()

    return len(notifications)


# =========================================================
# COMPATIBILITY ALIASES
# =========================================================
#
# These aliases allow either naming convention to be used
# by existing router code.
#

create_notification_service = create_notification

get_notifications_service = get_notifications

get_notification_service = get_notification

mark_notification_as_read_service = (
    mark_notification_as_read
)

mark_all_notifications_as_read_service = (
    mark_all_notifications_as_read
)