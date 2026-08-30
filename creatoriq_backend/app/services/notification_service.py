from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationCreate
from app.services.email_service import send_email


# ============================================================
# BASIC NOTIFICATION OPERATIONS
# ============================================================

def get_user_notifications(
    db: Session,
    user_id: int
):
    """
    Get all notifications belonging to the authenticated user.
    """

    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )


def get_notification_by_id(
    db: Session,
    notification_id: int,
    user_id: int
):
    """
    Get one notification belonging to the authenticated user.
    """

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        )
        .first()
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return notification


def create_notification(
    db: Session,
    notification_data: NotificationCreate
):
    """
    Create a new notification.

    The notification is saved to the database first.
    An email is then attempted for the notification owner.
    """

    notification = Notification(
        user_id=notification_data.user_id,
        contract_id=notification_data.contract_id,
        obligation_id=notification_data.obligation_id,
        notification_type=notification_data.notification_type,
        title=notification_data.title,
        message=notification_data.message,
        status="Unread",
        scheduled_at=notification_data.scheduled_at,
        sent_at=None,
        read_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    # --------------------------------------------------------
    # Send email notification
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(User.id == notification.user_id)
        .first()
    )

    if user:
        email_sent = send_email(
            to_email=user.email,
            subject=notification.title,
            body=notification.message,
        )

        if email_sent:
            notification.sent_at = datetime.utcnow()
            notification.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(notification)

    return notification


def mark_notification_as_read(
    db: Session,
    notification_id: int,
    user_id: int
):
    """
    Mark one notification as read.

    Only the owner of the notification can update it.
    """

    notification = get_notification_by_id(
        db,
        notification_id,
        user_id
    )

    if notification.status == "Unread":
        notification.status = "Read"
        notification.read_at = datetime.utcnow()
        notification.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(notification)

    return notification


def mark_all_notifications_as_read(
    db: Session,
    user_id: int
):
    """
    Mark all unread notifications belonging
    to the authenticated user as read.
    """

    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.status == "Unread"
        )
        .all()
    )

    current_time = datetime.utcnow()

    for notification in notifications:
        notification.status = "Read"
        notification.read_at = current_time
        notification.updated_at = current_time

    db.commit()

    return {
        "message": "All notifications marked as read",
        "updated_count": len(notifications)
    }


# ============================================================
# AUTOMATIC NOTIFICATION HELPERS
# ============================================================

def create_renewal_reminder(
    db: Session,
    renewal,
):
    """
    Create a notification for an upcoming renewal
    and attempt to send an email to the assigned user.
    """

    notification = Notification(
        user_id=renewal.assigned_to,
        contract_id=renewal.contract_id,
        obligation_id=None,
        notification_type="Renewal Reminder",
        title="Renewal Reminder",
        message=(
            "A contract renewal is approaching "
            "and requires your attention."
        ),
        status="Unread",
        scheduled_at=None,
        sent_at=None,
        read_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    _send_notification_email(
        db,
        notification
    )

    return notification


def create_obligation_due_notification(
    db: Session,
    obligation,
):
    """
    Create a notification for an upcoming obligation
    and attempt to send an email to the assigned user.
    """

    notification = Notification(
        user_id=obligation.assigned_to,
        contract_id=obligation.contract_id,
        obligation_id=obligation.id,
        notification_type="Obligation Due",
        title="Obligation Due",
        message=(
            f"Obligation '{obligation.title}' "
            "is approaching its due date."
        ),
        status="Unread",
        scheduled_at=None,
        sent_at=None,
        read_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    _send_notification_email(
        db,
        notification
    )

    return notification


def create_obligation_overdue_notification(
    db: Session,
    obligation,
):
    """
    Create a notification for an overdue obligation
    and attempt to send an email to the assigned user.
    """

    notification = Notification(
        user_id=obligation.assigned_to,
        contract_id=obligation.contract_id,
        obligation_id=obligation.id,
        notification_type="Obligation Overdue",
        title="Obligation Overdue",
        message=(
            f"Obligation '{obligation.title}' "
            "is overdue and requires immediate attention."
        ),
        status="Unread",
        scheduled_at=None,
        sent_at=None,
        read_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    _send_notification_email(
        db,
        notification
    )

    return notification


def create_compliance_alert(
    db: Session,
    contract,
    user_id: int,
    compliance_status: str,
):
    """
    Create a notification for a non-compliant
    or high-risk contract and attempt to send
    an email to the specified user.
    """

    notification = Notification(
        user_id=user_id,
        contract_id=contract.id,
        obligation_id=None,
        notification_type="Compliance Alert",
        title="Compliance Alert",
        message=(
            f"Contract {contract.contract_number} "
            f"is currently {compliance_status} "
            "and requires attention."
        ),
        status="Unread",
        scheduled_at=None,
        sent_at=None,
        read_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    _send_notification_email(
        db,
        notification
    )

    return notification


def create_contract_approval_notification(
    db: Session,
    contract,
    user_id: int,
):
    """
    Create a notification when a contract
    requires approval and attempt to send
    an email to the specified user.
    """

    notification = Notification(
        user_id=user_id,
        contract_id=contract.id,
        obligation_id=None,
        notification_type="Approval Required",
        title="Contract Approval Required",
        message=(
            f"Contract {contract.contract_number} "
            "is waiting for your approval."
        ),
        status="Unread",
        scheduled_at=None,
        sent_at=None,
        read_at=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    _send_notification_email(
        db,
        notification
    )

    return notification


# ============================================================
# INTERNAL EMAIL HELPER
# ============================================================

def _send_notification_email(
    db: Session,
    notification: Notification,
):
    """
    Send an email for a notification.

    Email failure does not prevent the database
    notification from existing.
    """

    user = (
        db.query(User)
        .filter(User.id == notification.user_id)
        .first()
    )

    if not user:
        return False

    email_sent = send_email(
        to_email=user.email,
        subject=notification.title,
        body=notification.message,
    )

    if email_sent:
        notification.sent_at = datetime.utcnow()
        notification.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(notification)

        return True

    return False