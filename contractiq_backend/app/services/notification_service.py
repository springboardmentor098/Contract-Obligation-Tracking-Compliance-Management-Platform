# from datetime import date, datetime

# from sqlalchemy.orm import Session

# from app.models.notification import Notification
# from app.models.contract import Contract
# from app.models.obligation import Obligation


# ALLOWED_NOTIFICATION_TYPES = {
#     "Renewal Reminder",
#     "Obligation Due Alert",
#     "Obligation Overdue Alert",
#     "Compliance Alert",
#     "Contract Approval Alert",
#     "Contract Status Alert",
# }


# RENEWAL_REMINDER_DAYS = {90, 60, 30, 7}
# OBLIGATION_DUE_ALERT_DAYS = 7

# def create_notification(
#     db: Session,
#     user_id: int,
#     title: str,
#     message: str,
#     notification_type: str,
#     contract_id: int | None = None,
#     obligation_id: int | None = None,
#     renewal_id: int | None = None,
#     scheduled_at: datetime | None = None,
# ):
#     if notification_type not in ALLOWED_NOTIFICATION_TYPES:
#         raise ValueError("Invalid notification type")

#     notification = Notification(
#         user_id=user_id,
#         contract_id=contract_id,
#         obligation_id=obligation_id,
#         renewal_id=renewal_id,
#         notification_type=notification_type,
#         title=title,
#         message=message,
#         status="Unread",
#         scheduled_at=scheduled_at,
#     )

#     db.add(notification)
#     db.commit()
#     db.refresh(notification)

#     return notification


# def generate_renewal_reminders(
#     db: Session
# ):
#     today = date.today()

#     contracts = (
#         db.query(Contract)
#         .filter(
#             Contract.end_date >= today,
#             Contract.status == "Active"
#         )
#         .all()
#     )

#     created_notifications = []

#     for contract in contracts:

#         days_until_expiry = (
#             contract.end_date - today
#         ).days

#         if days_until_expiry not in RENEWAL_REMINDER_DAYS:
#             continue

#         user_id = contract.assigned_to or contract.owner_id

#         existing_notification = (
#             db.query(Notification)
#             .filter(
#                 Notification.contract_id == contract.id,
#                 Notification.user_id == user_id,
#                 Notification.notification_type == "Renewal Reminder",
#                 Notification.created_at >= datetime.combine(
#                     today,
#                     datetime.min.time()
#                 )
#             )
#             .first()
#         )

#         if existing_notification:
#             continue

#         notification = create_notification(
#             db=db,
#             user_id=user_id,
#             contract_id=contract.id,
#             title="Contract Renewal Approaching",
#             message=(
#                 f"Contract {contract.contract_code} "
#                 f"expires in {days_until_expiry} days."
#             ),
#             notification_type="Renewal Reminder"
#         )

#         created_notifications.append(notification)

#     return created_notifications

from datetime import date, datetime
import smtplib
from email.message import EmailMessage
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.notification import Notification
from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.user import User


ALLOWED_NOTIFICATION_TYPES = {
    "Renewal Reminder",
    "Obligation Due Alert",
    "Obligation Overdue Alert",
    "Compliance Alert",
    "Contract Approval Alert",
    "Contract Status Alert",
}


RENEWAL_REMINDER_DAYS = {90, 60, 30, 7}
OBLIGATION_DUE_ALERT_DAYS = 7

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

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise ValueError("User not found")

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

    email_sent = send_notification_email(
        recipient_email=user.email,
        subject=title,
        message=message
    )

    if email_sent:
        notification.sent_at = datetime.utcnow()
        db.commit()
        db.refresh(notification)

    return notification

def generate_renewal_reminders(
    db: Session
):
    today = date.today()

    contracts = (
        db.query(Contract)
        .filter(
            Contract.end_date >= today,
            Contract.status == "Active"
        )
        .all()
    )

    created_notifications = []

    for contract in contracts:

        days_until_expiry = (
            contract.end_date - today
        ).days

        if days_until_expiry not in RENEWAL_REMINDER_DAYS:
            continue

        user_id = contract.assigned_to or contract.owner_id

        existing_notification = (
            db.query(Notification)
            .filter(
                Notification.contract_id == contract.id,
                Notification.user_id == user_id,
                Notification.notification_type == "Renewal Reminder",
                Notification.created_at >= datetime.combine(
                    today,
                    datetime.min.time()
                )
            )
            .first()
        )

        if existing_notification:
            continue

        notification = create_notification(
            db=db,
            user_id=user_id,
            contract_id=contract.id,
            title="Contract Renewal Approaching",
            message=(
                f"Contract {contract.contract_code} "
                f"expires in {days_until_expiry} days."
            ),
            notification_type="Renewal Reminder"
        )

        created_notifications.append(notification)

    return created_notifications


def generate_obligation_alerts(
    db: Session
):
    today = date.today()

    obligations = (
        db.query(Obligation)
        .filter(
            Obligation.status != "Completed"
        )
        .all()
    )

    created_notifications = []

    for obligation in obligations:

        days_until_due = (
            obligation.due_date - today
        ).days

        if days_until_due == OBLIGATION_DUE_ALERT_DAYS:
            notification_type = "Obligation Due Alert"

            title = "Obligation Due Soon"

            message = (
                f"Obligation '{obligation.title}' "
                f"is due in {OBLIGATION_DUE_ALERT_DAYS} days."
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

        existing_notification = (
            db.query(Notification)
            .filter(
                Notification.obligation_id == obligation.id,
                Notification.user_id == obligation.assigned_to,
                Notification.notification_type == notification_type,
                Notification.created_at >= datetime.combine(
                    today,
                    datetime.min.time()
                )
            )
            .first()
        )

        if existing_notification:
            continue

        notification = create_notification(
            db=db,
            user_id=obligation.assigned_to,
            contract_id=obligation.contract_id,
            obligation_id=obligation.id,
            title=title,
            message=message,
            notification_type=notification_type
        )

        created_notifications.append(notification)

    return created_notifications

def notify_contract_submitted_for_review(
    db: Session,
    contract: Contract
):
    legal_managers = (
        db.query(User)
        .filter(
            User.role.in_([
                "LEGAL_MANAGER",
                "ADMINISTRATOR"
            ]),
            User.is_active == True
        )
        .all()
    )

    created_notifications = []

    for user in legal_managers:

        existing_notification = (
            db.query(Notification)
            .filter(
                Notification.user_id == user.id,
                Notification.contract_id == contract.id,
                Notification.notification_type == "Contract Approval Alert",
                Notification.title == "Contract Submitted for Review",
                Notification.created_at >= datetime.combine(
                    date.today(),
                    datetime.min.time()
                )
            )
            .first()
        )

        if existing_notification:
            continue

        notification = create_notification(
            db=db,
            user_id=user.id,
            contract_id=contract.id,
            title="Contract Submitted for Review",
            message=(
                f"Contract {contract.contract_code} "
                f"has been submitted for review."
            ),
            notification_type="Contract Approval Alert"
        )

        created_notifications.append(notification)

    return created_notifications

def generate_compliance_alerts(
    db: Session
):
    contracts = db.query(Contract).all()

    created_notifications = []

    for contract in contracts:

        compliance = calculate_contract_compliance(
            contract.id,
            db
        )

        if compliance["compliance_status"] not in {
            "Non-Compliant",
            "High Risk"
        }:
            continue

        user_id = contract.assigned_to or contract.owner_id

        existing_notification = (
            db.query(Notification)
            .filter(
                Notification.contract_id == contract.id,
                Notification.user_id == user_id,
                Notification.notification_type == "Compliance Alert",
                Notification.created_at >= datetime.combine(
                    date.today(),
                    datetime.min.time()
                )
            )
            .first()
        )

        if existing_notification:
            continue

        notification = create_notification(
            db=db,
            user_id=user_id,
            contract_id=contract.id,
            title="High-Risk Contract Detected",
            message=(
                f"Contract {contract.contract_code} has "
                f"{compliance['overdue_obligations']} overdue "
                f"obligation(s) and requires attention."
            ),
            notification_type="Compliance Alert"
        )

        created_notifications.append(notification)

    return created_notifications


def notify_contract_approved(
    db: Session,
    contract: Contract
):
    user_ids = set()

    if contract.owner_id:
        user_ids.add(contract.owner_id)

    if contract.assigned_to:
        user_ids.add(contract.assigned_to)

    created_notifications = []

    for user_id in user_ids:

        existing_notification = (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.contract_id == contract.id,
                Notification.notification_type == "Contract Approval Alert",
                Notification.title == "Contract Approved",
                Notification.created_at >= datetime.combine(
                    date.today(),
                    datetime.min.time()
                )
            )
            .first()
        )

        if existing_notification:
            continue

        notification = create_notification(
            db=db,
            user_id=user_id,
            contract_id=contract.id,
            title="Contract Approved",
            message=(
                f"Contract {contract.contract_code} "
                f"has been approved."
            ),
            notification_type="Contract Approval Alert"
        )

        created_notifications.append(notification)

    return created_notifications


def notify_contract_status_changed(
    db: Session,
    contract: Contract,
    old_status: str,
    new_status: str
):
    user_ids = set()

    if contract.owner_id:
        user_ids.add(contract.owner_id)

    if contract.assigned_to:
        user_ids.add(contract.assigned_to)

    created_notifications = []

    for user_id in user_ids:
        existing_notification = (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.contract_id == contract.id,
                Notification.notification_type == "Contract Status Alert",
                Notification.title == f"Contract Status Changed to {new_status}",
                Notification.created_at >= datetime.combine(
                    date.today(),
                    datetime.min.time()
                )
            )
            .first()
        )

        if existing_notification:
            continue

        notification = create_notification(
            db=db,
            user_id=user_id,
            contract_id=contract.id,
            title=f"Contract Status Changed to {new_status}",
            message=(
                f"Contract {contract.contract_code} "
                f"status changed from {old_status} "
                f"to {new_status}."
            ),
            notification_type="Contract Status Alert"
        )

        created_notifications.append(notification)

    return created_notifications

def send_notification_email(
    recipient_email: str,
    subject: str,
    message: str
):
    email = EmailMessage()

    email["From"] = settings.SMTP_USERNAME
    email["To"] = recipient_email
    email["Subject"] = subject

    email.set_content(message)

    try:
        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT
        ) as smtp:

            smtp.starttls()

            smtp.login(
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD
            )

            smtp.send_message(email)

        return True

    except Exception as exc:
        print(
            f"Failed to send notification email: {exc}"
        )
        return False