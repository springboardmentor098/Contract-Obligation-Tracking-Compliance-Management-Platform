from datetime import date, datetime, timedelta
import os
import smtplib
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User
from app.models.contract import Contract
from app.models.obligation import Obligation


# ============================================================
# NOTIFICATION TYPES
# ============================================================

NOTIFICATION_TYPES = {
    "Renewal Reminder",
    "Obligation Due Alert",
    "Obligation Overdue Alert",
    "Compliance Alert",
    "Contract Approval Alert",
    "Contract Status Alert",
}


# ============================================================
# NOTIFICATION STATUS
# ============================================================

NOTIFICATION_STATUSES = {
    "Unread",
    "Read",
}


# ============================================================
# CREATE NOTIFICATION
# ============================================================

def create_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    contract_id: int = None,
    obligation_id: int = None,
    scheduled_at: datetime = None,
):
    """
    Create a new notification for a user.
    """

    # --------------------------------------------------------
    # Validate notification type
    # --------------------------------------------------------

    if notification_type not in NOTIFICATION_TYPES:
        raise ValueError(
            "Invalid notification type. Allowed types: "
            + ", ".join(NOTIFICATION_TYPES)
        )

    # --------------------------------------------------------
    # Check user exists
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        return None

    # --------------------------------------------------------
    # Create notification
    # --------------------------------------------------------

    notification = Notification(
        user_id=user_id,
        contract_id=contract_id,
        obligation_id=obligation_id,
        notification_type=notification_type,
        title=title,
        message=message,
        status="Unread",
        scheduled_at=scheduled_at,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


# ============================================================
# MARK NOTIFICATION AS READ
# ============================================================

def mark_notification_as_read(
    db: Session,
    notification: Notification
):
    """
    Change notification status from Unread to Read.
    """

    if notification.status == "Unread":

        notification.status = "Read"
        notification.read_at = datetime.utcnow()
        notification.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(notification)

    return notification


# ============================================================
# MARK ALL NOTIFICATIONS AS READ
# ============================================================

def mark_all_notifications_as_read(
    db: Session,
    user_id: int
):
    """
    Mark all unread notifications of a user as read.
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

    return len(notifications)


# ============================================================
# CHECK IF NOTIFICATION ALREADY EXISTS
# ============================================================

def notification_exists(
    db: Session,
    user_id: int,
    notification_type: str,
    contract_id: int = None,
    obligation_id: int = None,
):
    """
    Prevent duplicate notifications for the same event.
    """

    query = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.notification_type == notification_type,
        )
    )

    if contract_id is not None:

        query = query.filter(
            Notification.contract_id == contract_id
        )

    if obligation_id is not None:

        query = query.filter(
            Notification.obligation_id == obligation_id
        )

    return query.first() is not None


# ============================================================
# RENEWAL REMINDERS
# ============================================================

def generate_renewal_reminders(
    db: Session
):
    """
    Generate renewal reminders for contracts approaching expiry.

    Reminder intervals:
        90 days
        60 days
        30 days
        7 days
    """

    reminder_days = [90, 60, 30, 7]

    today = date.today()

    contracts = (
        db.query(Contract)
        .filter(
            Contract.end_date.isnot(None)
        )
        .all()
    )

    generated_notifications = []

    for contract in contracts:

        days_remaining = (
            contract.end_date - today
        ).days

        if days_remaining not in reminder_days:
            continue

        # ----------------------------------------------------
        # Determine recipient
        # ----------------------------------------------------

        user_id = contract.assigned_to

        if user_id is None:
            user_id = contract.created_by

        if user_id is None:
            continue

        # ----------------------------------------------------
        # Prevent duplicates
        # ----------------------------------------------------

        if notification_exists(
            db,
            user_id,
            "Renewal Reminder",
            contract_id=contract.id
        ):
            continue

        # ----------------------------------------------------
        # Create notification
        # ----------------------------------------------------

        notification = create_notification(
            db=db,
            user_id=user_id,
            contract_id=contract.id,
            notification_type="Renewal Reminder",
            title="Contract Renewal Approaching",
            message=(
                f"{contract.title} "
                f"({contract.contract_number}) "
                f"expires in {days_remaining} days."
            )
        )

        if notification:
            generated_notifications.append(notification)

    return generated_notifications


# ============================================================
# OBLIGATION DUE ALERTS
# ============================================================

def generate_obligation_due_alerts(
    db: Session
):
    """
    Generate alerts for obligations due within 7 days.
    """

    today = date.today()
    alert_date = today + timedelta(days=7)

    obligations = (
        db.query(Obligation)
        .filter(
            Obligation.status.in_(
                ["Pending", "In Progress"]
            ),
            Obligation.due_date >= today,
            Obligation.due_date <= alert_date
        )
        .all()
    )

    generated_notifications = []

    for obligation in obligations:

        if obligation.assigned_to is None:
            continue

        days_remaining = (
            obligation.due_date - today
        ).days

        if notification_exists(
            db,
            obligation.assigned_to,
            "Obligation Due Alert",
            contract_id=obligation.contract_id,
            obligation_id=obligation.id
        ):
            continue

        notification = create_notification(
            db=db,
            user_id=obligation.assigned_to,
            contract_id=obligation.contract_id,
            obligation_id=obligation.id,
            notification_type="Obligation Due Alert",
            title="Obligation Due Soon",
            message=(
                f"Obligation '{obligation.title}' "
                f"is due in {days_remaining} days."
            )
        )

        if notification:
            generated_notifications.append(notification)

    return generated_notifications


# ============================================================
# OVERDUE OBLIGATION ALERTS
# ============================================================

def generate_overdue_alerts(
    db: Session
):
    """
    Generate alerts for overdue obligations.
    """

    today = date.today()

    obligations = (
        db.query(Obligation)
        .filter(
            Obligation.due_date < today,
            Obligation.status != "Completed"
        )
        .all()
    )

    generated_notifications = []

    for obligation in obligations:

        if obligation.assigned_to is None:
            continue

        # ----------------------------------------------------
        # Update obligation status
        # ----------------------------------------------------

        if obligation.status != "Overdue":
            obligation.status = "Overdue"
            obligation.updated_at = datetime.utcnow()

        # ----------------------------------------------------
        # Prevent duplicate notification
        # ----------------------------------------------------

        if notification_exists(
            db,
            obligation.assigned_to,
            "Obligation Overdue Alert",
            contract_id=obligation.contract_id,
            obligation_id=obligation.id
        ):
            continue

        # ----------------------------------------------------
        # Create notification
        # ----------------------------------------------------

        notification = create_notification(
            db=db,
            user_id=obligation.assigned_to,
            contract_id=obligation.contract_id,
            obligation_id=obligation.id,
            notification_type="Obligation Overdue Alert",
            title="Obligation Overdue",
            message=(
                f"Obligation '{obligation.title}' "
                f"for contract ID {obligation.contract_id} "
                f"is overdue."
            )
        )

        if notification:
            generated_notifications.append(notification)

    db.commit()

    return generated_notifications


# ============================================================
# COMPLIANCE ALERT
# ============================================================

def generate_compliance_alert(
    db: Session,
    contract_id: int,
    compliance_status: str,
    risk_level: str,
    overdue_obligations: int,
):
    """
    Generate compliance notification for a contract.

    High risk:
        Notify Compliance Officers.

    Non-compliant:
        Notify Compliance Officers.
    """

    if (
        compliance_status != "Non-Compliant"
        and risk_level != "High"
    ):
        return []

    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        return []

    # --------------------------------------------------------
    # Find Compliance Officers
    # --------------------------------------------------------

    compliance_officers = (
        db.query(User)
        .filter(
            User.role == "Compliance Officer",
            User.is_active == True
        )
        .all()
    )

    generated_notifications = []

    for officer in compliance_officers:

        if notification_exists(
            db,
            officer.id,
            "Compliance Alert",
            contract_id=contract.id
        ):
            continue

        if risk_level == "High":

            title = "High-Risk Contract Detected"

            message = (
                f"Contract {contract.contract_number} "
                f"has {overdue_obligations} overdue obligations "
                f"and requires immediate attention."
            )

        else:

            title = "Contract Compliance Alert"

            message = (
                f"Contract {contract.contract_number} "
                f"is currently {compliance_status}."
            )

        notification = create_notification(
            db=db,
            user_id=officer.id,
            contract_id=contract.id,
            notification_type="Compliance Alert",
            title=title,
            message=message
        )

        if notification:
            generated_notifications.append(notification)

    return generated_notifications


# ============================================================
# CONTRACT APPROVAL NOTIFICATION
# ============================================================

def generate_approval_notification(
    db: Session,
    contract_id: int,
    approved_by_user_id: int = None
):
    """
    Generate contract approval notification.

    The notification is sent to the contract creator.
    """

    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        return None

    recipient_id = contract.created_by

    if recipient_id is None:
        return None

    # --------------------------------------------------------
    # Prevent duplicate
    # --------------------------------------------------------

    if notification_exists(
        db,
        recipient_id,
        "Contract Approval Alert",
        contract_id=contract.id
    ):
        return None

    notification = create_notification(
        db=db,
        user_id=recipient_id,
        contract_id=contract.id,
        notification_type="Contract Approval Alert",
        title="Contract Approved",
        message=(
            f"Contract {contract.contract_number} "
            f"has been approved."
        )
    )

    return notification


# ============================================================
# CONTRACT STATUS NOTIFICATION
# ============================================================

def generate_status_notification(
    db: Session,
    contract_id: int,
    new_status: str
):
    """
    Notify the assigned user when contract status changes.
    """

    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        return None

    recipient_id = contract.assigned_to

    if recipient_id is None:
        return None

    if notification_exists(
        db,
        recipient_id,
        "Contract Status Alert",
        contract_id=contract.id
    ):
        return None

    notification = create_notification(
        db=db,
        user_id=recipient_id,
        contract_id=contract.id,
        notification_type="Contract Status Alert",
        title="Contract Status Updated",
        message=(
            f"Contract {contract.contract_number} "
            f"status has changed to '{new_status}'."
        )
    )

    return notification


# ============================================================
# SMTP EMAIL
# ============================================================

def send_email_notification(
    user_email: str,
    subject: str,
    body: str
):
    """
    Send notification email using SMTP.

    SMTP configuration comes from environment variables.
    """

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")

    # --------------------------------------------------------
    # Check SMTP configuration
    # --------------------------------------------------------

    if not all([
        smtp_host,
        smtp_port,
        smtp_username,
        smtp_password
    ]):
        return False

    try:

        smtp_port = int(smtp_port)

        email = EmailMessage()

        email["From"] = smtp_username
        email["To"] = user_email
        email["Subject"] = subject

        email.set_content(body)

        with smtplib.SMTP(
            smtp_host,
            smtp_port,
            timeout=10
        ) as server:

            server.starttls()

            server.login(
                smtp_username,
                smtp_password
            )

            server.send_message(email)

        return True

    except Exception as error:

        print(
            f"Email notification failed: {error}"
        )

        return False