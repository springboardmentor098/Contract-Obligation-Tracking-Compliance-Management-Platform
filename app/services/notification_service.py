from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User
from app.models.contract import Contract
from app.models.obligation import Obligation
from app.services.email_service import send_email


NOTIFICATION_TYPES = {
    "Renewal Reminder",
    "Obligation Due Alert",
    "Obligation Overdue Alert",
    "Compliance Alert",
    "Contract Approval Alert",
    "Contract Status Alert",
}


def now_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)


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
    if notification_type not in NOTIFICATION_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification type",
        )

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if contract_id is not None:
        contract = db.query(Contract).filter(
            Contract.id == contract_id
        ).first()

        if contract is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found",
            )

    if obligation_id is not None:
        obligation = db.query(Obligation).filter(
            Obligation.id == obligation_id
        ).first()

        if obligation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Obligation not found",
            )

    current_time = now_utc()

    notification = Notification(
        user_id=user_id,
        contract_id=contract_id,
        obligation_id=obligation_id,
        notification_type=notification_type,
        title=title,
        message=message,
        status="Unread",
        scheduled_at=scheduled_at,
        sent_at=None,
        read_at=None,
        created_at=current_time,
        updated_at=current_time,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    # Send email without breaking notification creation if email fails.
    try:
        if user.email:
            email_sent = send_email(
                to_email=user.email,
                subject=title,
                body=message,
            )

            if email_sent:
                notification.sent_at = now_utc()
                notification.updated_at = now_utc()
                db.commit()
                db.refresh(notification)

    except Exception as exc:
        print(f"Notification email failed: {exc}")

    return notification


def mark_notification_read(
    notification: Notification,
    db: Session,
):
    current_time = now_utc()

    notification.status = "Read"
    notification.read_at = current_time
    notification.updated_at = current_time

    db.commit()
    db.refresh(notification)

    return notification


def mark_all_notifications_read(
    user_id: int,
    db: Session,
):
    current_time = now_utc()

    notifications = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.status == "Unread",
    ).all()

    for notification in notifications:
        notification.status = "Read"
        notification.read_at = current_time
        notification.updated_at = current_time

    db.commit()

    return len(notifications)


def generate_renewal_reminders(
    db: Session,
):
    """
    Generate renewal reminders for contracts expiring in:
    90, 60, 30, or 7 days.
    """

    today = date.today()
    reminder_days = {90, 60, 30, 7}

    contracts = db.query(Contract).all()
    created = []

    for contract in contracts:
        days_until_expiry = (contract.end_date - today).days

        if days_until_expiry not in reminder_days:
            continue

        if contract.assigned_to is None:
            user_id = contract.created_by
        else:
            user_id = contract.assigned_to

        existing = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.contract_id == contract.id,
            Notification.notification_type == "Renewal Reminder",
            Notification.message.contains(
                f"{days_until_expiry} days"
            ),
        ).first()

        if existing:
            continue

        notification = create_notification(
            db=db,
            user_id=user_id,
            contract_id=contract.id,
            notification_type="Renewal Reminder",
            title="Contract Renewal Approaching",
            message=(
                f"Contract {contract.contract_number} "
                f"expires in {days_until_expiry} days."
            ),
        )

        created.append(notification)

    return created


def generate_obligation_alerts(
    db: Session,
):
    """
    Generate due-date alerts 7 days before an obligation
    and overdue alerts once the due date has passed.
    """

    today = date.today()

    obligations = db.query(Obligation).all()
    created = []

    for obligation in obligations:

        if obligation.status == "Completed":
            continue

        days_until_due = (obligation.due_date - today).days

        if days_until_due == 7:
            notification_type = "Obligation Due Alert"
            title = "Obligation Due Soon"
            message = (
                f"Obligation '{obligation.title}' "
                f"is due in 7 days."
            )

        elif days_until_due < 0:
            notification_type = "Obligation Overdue Alert"
            title = "Obligation Overdue"
            message = (
                f"Obligation '{obligation.title}' "
                f"is overdue."
            )

        else:
            continue

        existing = db.query(Notification).filter(
            Notification.user_id == obligation.assigned_to,
            Notification.obligation_id == obligation.id,
            Notification.notification_type == notification_type,
        ).first()

        if existing:
            continue

        notification = create_notification(
            db=db,
            user_id=obligation.assigned_to,
            contract_id=obligation.contract_id,
            obligation_id=obligation.id,
            notification_type=notification_type,
            title=title,
            message=message,
        )

        created.append(notification)

    return created


def generate_compliance_alert(
    db: Session,
    contract_id: int,
    user_id: int,
    risk_level: str,
    overdue_obligations: int,
):
    title = "Compliance Alert"

    if risk_level == "High":
        title = "High-Risk Contract Detected"

    message = (
        f"Contract {contract_id} requires compliance attention. "
        f"Risk level: {risk_level}. "
        f"Overdue obligations: {overdue_obligations}."
    )

    return create_notification(
        db=db,
        user_id=user_id,
        contract_id=contract_id,
        notification_type="Compliance Alert",
        title=title,
        message=message,
    )


def generate_contract_approval_notification(
    db: Session,
    contract: Contract,
    user_id: int,
):
    return create_notification(
        db=db,
        user_id=user_id,
        contract_id=contract.id,
        notification_type="Contract Approval Alert",
        title="Contract Submitted for Review",
        message=(
            f"Contract {contract.contract_number} "
            f"has been submitted for review."
        ),
    )


def generate_contract_status_notification(
    db: Session,
    contract: Contract,
    user_id: int,
):
    return create_notification(
        db=db,
        user_id=user_id,
        contract_id=contract.id,
        notification_type="Contract Status Alert",
        title="Contract Status Updated",
        message=(
            f"Contract {contract.contract_number} "
            f"status is now {contract.status}."
        ),
    )
