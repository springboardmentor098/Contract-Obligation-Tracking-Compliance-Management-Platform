from datetime import datetime, date

from sqlalchemy.orm import Session

from backend.app.models.notification import Notification
from backend.app.models.renewal import Renewal
from backend.app.models.contract import Contract
from backend.app.models.obligation import Obligation
from backend.app.models.user import User
from backend.app.services.email_service import send_email

def create_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    contract_id: int | None = None,
    obligation_id: int | None = None,
):
    notification = Notification(
        user_id=user_id,
        contract_id=contract_id,
        obligation_id=obligation_id,
        notification_type=notification_type,
        title=title,
        message=message,
        status="Unread",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    print("DEBUG: create_notification called")

    # Find recipient user
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    print(
        "DEBUG: user =",
        user.email if user else None
    )

    # Send email
    if user and user.email:

        print("DEBUG: calling send_email")

        email_sent = send_email(
            to_email=user.email,
            subject=title,
            message=message
        )

        print(
            "DEBUG: email_sent =",
            email_sent
        )

        if email_sent:
            notification.sent_at = datetime.utcnow()
            notification.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(notification)

    return notification


def create_renewal_reminder(
    db: Session,
    user_id: int,
    contract_id: int,
    contract_number: str,
    days_remaining: int,
):
    return create_notification(
        db=db,
        user_id=user_id,
        contract_id=contract_id,
        notification_type="Renewal Reminder",
        title="Contract Renewal Approaching",
        message=(
            f"Contract {contract_number} expires in "
            f"{days_remaining} days."
        ),
    )


def check_renewal_reminders(db: Session):
    today = date.today()

    renewals = db.query(Renewal).all()

    created_notifications = []

    reminder_days = [90, 60, 30, 7]

    for renewal in renewals:

        if not renewal.renewal_date:
            continue

        days_remaining = (
            renewal.renewal_date - today
        ).days
        print(
    "DEBUG:",
    "renewal_id =", renewal.id,
    "renewal_date =", renewal.renewal_date,
    "today =", today,
    "days_remaining =", days_remaining
    )   

        if days_remaining not in reminder_days:
            continue

        contract = db.query(Contract).filter(
            Contract.id == renewal.contract_id
        ).first()

        if not contract:
            continue

        user_id = contract.assigned_to or contract.owner_id

        # Avoid duplicate reminder
        existing_notification = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.contract_id == contract.id,
            Notification.notification_type == "Renewal Reminder",
            Notification.message == (
                f"Contract {contract.contract_number} expires in "
                f"{days_remaining} days."
            )
        ).first()

        if existing_notification:
            continue

        notification = create_renewal_reminder(
            db=db,
            user_id=user_id,
            contract_id=contract.id,
            contract_number=contract.contract_number,
            days_remaining=days_remaining,
        )

        created_notifications.append(notification)

    return created_notifications
def check_obligation_due_reminders(db: Session):
    today = date.today()

    obligations = db.query(Obligation).all()

    created_notifications = []

    for obligation in obligations:

        if not obligation.due_date:
            continue

        days_remaining = (
            obligation.due_date - today
        ).days

        print(
            f"DEBUG DUE: obligation_id={obligation.id}, "
            f"due_date={obligation.due_date}, "
            f"today={today}, "
            f"days_remaining={days_remaining}, "
            f"status={obligation.status}, "
            f"assigned_to={obligation.assigned_to}"
        )

        if days_remaining != 7:
            continue

        contract = db.query(Contract).filter(
            Contract.id == obligation.contract_id
        ).first()

        if not contract:
            continue

        user_id = obligation.assigned_to

        if not user_id:
            user_id = contract.assigned_to or contract.owner_id

        if not user_id:
            continue

        message = (
            f"Obligation {obligation.title} for "
            f"Contract {contract.contract_number} "
            f"is due in 7 days."
        )

        existing_notification = db.query(
            Notification
        ).filter(
            Notification.user_id == user_id,
            Notification.contract_id == contract.id,
            Notification.obligation_id == obligation.id,
            Notification.notification_type == "Obligation Due Alert"
        ).first()

        if existing_notification:
            continue

        notification = create_notification(
            db=db,
            user_id=user_id,
            contract_id=contract.id,
            obligation_id=obligation.id,
            notification_type="Obligation Due Alert",
            title="Obligation Due Soon",
            message=message,
        )

        created_notifications.append(notification)

    return created_notifications
def create_compliance_alert(
    db: Session,
    user_id: int,
    contract_id: int,
    contract_number: str,
    message: str,
):
    return create_notification(
        db=db,
        user_id=user_id,
        contract_id=contract_id,
        notification_type="Compliance Alert",
        title="High-Risk Contract Detected",
        message=message,
    )
def check_compliance_alerts(db: Session):
    contracts = db.query(Contract).all()

    created_notifications = []

    for contract in contracts:

        # Example: check overdue obligations
        overdue_count = db.query(Obligation).filter(
            Obligation.contract_id == contract.id,
            Obligation.status == "Overdue"
        ).count()

        if overdue_count == 0:
            continue

        user_id = contract.assigned_to or contract.owner_id

        if not user_id:
            continue

        message = (
            f"Contract {contract.contract_number} has "
            f"{overdue_count} overdue obligation(s) "
            f"and requires immediate attention."
        )

        # Avoid duplicate notification
        existing_notification = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.contract_id == contract.id,
            Notification.notification_type == "Compliance Alert",
            Notification.message == message,
            Notification.status == "Unread"
        ).first()

        if existing_notification:
            continue

        notification = create_compliance_alert(
            db=db,
            user_id=user_id,
            contract_id=contract.id,
            contract_number=contract.contract_number,
            message=message,
        )

        created_notifications.append(notification)

    return created_notifications
def create_approval_notification(
    db: Session,
    user_id: int,
    contract_id: int,
    contract_number: str,
):
    return create_notification(
        db=db,
        user_id=user_id,
        contract_id=contract_id,
        notification_type="Contract Approval Alert",
        title="Contract Submitted for Review",
        message=(
            f"Contract {contract_number} has been submitted "
            f"for review and approval."
        ),
    )


def create_contract_approved_notification(
    db: Session,
    user_id: int,
    contract_id: int,
    contract_number: str,
):
    return create_notification(
        db=db,
        user_id=user_id,
        contract_id=contract_id,
        notification_type="Contract Approval Alert",
        title="Contract Approved",
        message=(
            f"Contract {contract_number} has been approved."
        ),
    )