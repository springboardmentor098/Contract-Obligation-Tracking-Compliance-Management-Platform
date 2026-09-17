from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session
from app.services.email_service import send_notification_email
from app.models.contract import Contract
from app.models.notification import Notification
from app.models.obligation import Obligation


def create_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    contract_id: int | None = None,
    obligation_id: int | None = None,
    scheduled_at: datetime | None = None
):
    notification = Notification(
        user_id=user_id,
        contract_id=contract_id,
        obligation_id=obligation_id,
        notification_type=notification_type,
        title=title,
        message=message,
        status="Unread",
        scheduled_at=scheduled_at,
        sent_at=datetime.now()
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)
    send_notification_email(
        to_email=notification.user.email,
        subject=title,
        message=message
    )

    return notification


def generate_obligation_alerts(db: Session):
    today = date.today()
    due_alert_date = today + timedelta(days=7)

    obligations = db.query(Obligation).all()

    created_notifications = []

    for obligation in obligations:

        if obligation.status == "Completed":
            continue

        if obligation.due_date < today:
            notification = create_notification(
                db=db,
                user_id=obligation.assigned_to,
                contract_id=obligation.contract_id,
                obligation_id=obligation.id,
                notification_type="Obligation Overdue Alert",
                title="Obligation Overdue",
                message=f"Obligation '{obligation.title}' is overdue."
            )

            created_notifications.append(notification)

        elif obligation.due_date <= due_alert_date:
            notification = create_notification(
                db=db,
                user_id=obligation.assigned_to,
                contract_id=obligation.contract_id,
                obligation_id=obligation.id,
                notification_type="Obligation Due Alert",
                title="Obligation Due Soon",
                message=f"Obligation '{obligation.title}' is due within 7 days."
            )

            created_notifications.append(notification)

    return created_notifications
def generate_renewal_reminders(db: Session):
    today = date.today()

    reminder_intervals = [90, 60, 30, 7]

    contracts = db.query(Contract).all()

    created_notifications = []

    for contract in contracts:
        if not contract.assigned_to:
            continue

        days_until_expiry = (
            contract.end_date - today
        ).days

        if days_until_expiry in reminder_intervals:
            notification = create_notification(
                db=db,
                user_id=contract.assigned_to,
                contract_id=contract.id,
                notification_type="Renewal Reminder",
                title="Contract Renewal Approaching",
                message=(
                    f"Contract {contract.contract_number} "
                    f"expires in {days_until_expiry} days."
                )
            )

            created_notifications.append(notification)

    return created_notifications
def generate_compliance_alert(
    db: Session,
    contract: Contract,
    compliance_status: str,
    risk_level: str
):
    if compliance_status not in [
        "Non-Compliant",
        "High Risk"
    ]:
        return None

    if not contract.assigned_to:
        return None

    if compliance_status == "High Risk":
        title = "High-Risk Contract Detected"
        message = (
            f"Contract {contract.contract_number} has significant "
            f"compliance issues and requires immediate attention."
        )
    else:
        title = "Non-Compliant Contract Detected"
        message = (
            f"Contract {contract.contract_number} has compliance "
            f"issues and requires attention."
        )

    return create_notification(
        db=db,
        user_id=contract.assigned_to,
        contract_id=contract.id,
        notification_type="Compliance Alert",
        title=title,
        message=message
    )
def generate_contract_approval_notification(
    db: Session,
    contract: Contract,
    user_id: int
):
    return create_notification(
        db=db,
        user_id=user_id,
        contract_id=contract.id,
        notification_type="Contract Approval Alert",
        title="Contract Approved",
        message=(
            f"Contract {contract.contract_number} "
            f"has been approved successfully."
        )
    )
def generate_contract_approval_notification(
    db: Session,
    contract: Contract,
    user_id: int
):
    return create_notification(
        db=db,
        user_id=user_id,
        contract_id=contract.id,
        notification_type="Contract Approval Alert",
        title="Contract Approved",
        message=(
            f"Contract {contract.contract_number} "
            f"has been approved successfully."
        )
    )