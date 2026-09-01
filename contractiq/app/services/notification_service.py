"""
Notification service (Sprint 12, section 14).

Other services (Contract, Obligation, Renewal, Compliance) call into this
module instead of writing to the notifications table directly. This keeps
notification-generation logic in one reusable place.
"""

from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationType, NotificationStatus
from app.models.user import User
from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.renewal import Renewal
from app.config import settings
from app.services.email_service import send_email


def _create_notification(
    db: Session,
    user_id: int,
    notification_type: NotificationType,
    title: str,
    message: str,
    contract_id: Optional[int] = None,
    obligation_id: Optional[int] = None,
    send_email_now: bool = True,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        contract_id=contract_id,
        obligation_id=obligation_id,
        notification_type=notification_type,
        title=title,
        message=message,
        status=NotificationStatus.UNREAD,
    )
    db.add(notification)
    db.flush()

    if send_email_now:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            sent = send_email(user.email, title, message)
            if sent:
                notification.sent_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(notification)
    return notification


def notify_contract_status_change(db: Session, contract: Contract, recipient_user_id: int) -> Notification:
    title = f"Contract {contract.contract_number} status changed"
    message = f"Contract '{contract.title}' ({contract.contract_number}) status is now {contract.status.value}."
    return _create_notification(
        db, recipient_user_id, NotificationType.CONTRACT_STATUS_ALERT, title, message, contract_id=contract.id
    )


def notify_contract_submitted_for_review(db: Session, contract: Contract, legal_manager_ids: list[int]) -> None:
    title = "Contract Submitted for Review"
    message = f"Contract '{contract.title}' ({contract.contract_number}) has been submitted for review."
    for user_id in legal_manager_ids:
        _create_notification(
            db, user_id, NotificationType.CONTRACT_APPROVAL_ALERT, title, message, contract_id=contract.id
        )


def notify_contract_approved(db: Session, contract: Contract, recipient_user_id: int) -> Notification:
    title = "Contract Approved"
    message = f"Contract '{contract.title}' ({contract.contract_number}) has been approved."
    return _create_notification(
        db, recipient_user_id, NotificationType.CONTRACT_APPROVAL_ALERT, title, message, contract_id=contract.id
    )


def notify_obligation_due_soon(db: Session, obligation: Obligation) -> Optional[Notification]:
    if not obligation.assigned_to:
        return None
    title = "Obligation Due Soon"
    message = (
        f"Obligation '{obligation.title}' for contract ID {obligation.contract_id} "
        f"is due on {obligation.due_date.isoformat()}."
    )
    return _create_notification(
        db,
        obligation.assigned_to,
        NotificationType.OBLIGATION_DUE_ALERT,
        title,
        message,
        contract_id=obligation.contract_id,
        obligation_id=obligation.id,
    )


def notify_obligation_overdue(db: Session, obligation: Obligation) -> Optional[Notification]:
    if not obligation.assigned_to:
        return None
    title = "Obligation Overdue"
    message = (
        f"Obligation '{obligation.title}' for contract ID {obligation.contract_id} "
        f"was due on {obligation.due_date.isoformat()} and is now overdue."
    )
    return _create_notification(
        db,
        obligation.assigned_to,
        NotificationType.OBLIGATION_OVERDUE_ALERT,
        title,
        message,
        contract_id=obligation.contract_id,
        obligation_id=obligation.id,
    )


def notify_renewal_reminder(db: Session, renewal: Renewal, days_remaining: int) -> Optional[Notification]:
    if not renewal.assigned_to:
        return None
    title = "Contract Renewal Approaching"
    message = (
        f"Contract ID {renewal.contract_id} expires in {days_remaining} days "
        f"(expiry date {renewal.previous_expiry_date.isoformat()})."
    )
    return _create_notification(
        db,
        renewal.assigned_to,
        NotificationType.RENEWAL_REMINDER,
        title,
        message,
        contract_id=renewal.contract_id,
    )


def notify_compliance_alert(db: Session, contract: Contract, compliance_officer_ids: list[int], detail: str) -> None:
    title = f"Compliance Alert: {contract.contract_number}"
    for user_id in compliance_officer_ids:
        _create_notification(
            db, user_id, NotificationType.COMPLIANCE_ALERT, title, detail, contract_id=contract.id
        )
