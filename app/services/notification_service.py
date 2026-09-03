from datetime import date, datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import smtplib
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.contract import Contract
from app.models.notification import Notification
from app.models.obligation import Obligation
from app.models.user import User
from app.services import compliance_service

logger = logging.getLogger(__name__)


def send_smtp_email(to_email: str, subject: str, body: str) -> bool:
    """
    Sends an SMTP email notification gracefully.
    If SMTP server or credentials are unconfigured, skips delivery safely.
    """
    if not settings.SMTP_HOST or not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD or not to_email:
        logger.info(f"[SMTP Simulator] Email to '{to_email}' skipped: SMTP credentials not configured in environment.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = to_email

        text_part = MIMEText(body, "plain")
        msg.attach(text_part)

        # Attempt connection with STARTTLS
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=5) as server:
            server.ehlo()
            if settings.SMTP_PORT in [587, 25]:
                server.starttls()
                server.ehlo()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, [to_email], msg.as_string())
        
        logger.info(f"[SMTP Success] Email sent to {to_email}")
        return True
    except Exception as e:
        logger.warning(f"[SMTP Delivery Handled] Could not send email to {to_email}: {e}")
        return False



def create_notification(
    db: Session,
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    contract_id: Optional[int] = None,
    obligation_id: Optional[int] = None
) -> Notification:
    """
    Creates an in-app notification in database and triggers SMTP email.
    """
    # Verify recipient user exists
    recipient = db.query(User).filter((User.user_id == user_id) | (User.id == user_id)).first()
    if not recipient:
        recipient = db.query(User).first()

    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found."
        )


    new_notification = Notification(
        user_id=recipient.user_id,
        contract_id=contract_id,
        obligation_id=obligation_id,
        notification_type=notification_type,
        title=title.strip(),
        message=message.strip(),
        status="Unread",
        sent_at=datetime.utcnow()
    )

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)

    # Attempt SMTP email dispatch
    if recipient.email:
        send_smtp_email(recipient.email, f"[ContractIQ Alert] {title}", message)

    return new_notification


def generate_renewal_reminders(db: Session) -> List[Notification]:
    """
    Scans contracts expiring within 90, 60, 30, 7 days and creates Renewal Reminders.
    """
    today = date.today()
    target_max = today + timedelta(days=90)
    contracts = db.query(Contract).filter(
        Contract.end_date.isnot(None),
        Contract.end_date >= today,
        Contract.end_date <= target_max
    ).all()
    created_notifications = []

    intervals = [90, 60, 30, 7]

    for c in contracts:
        days_rem = (c.end_date - today).days
        if days_rem in intervals or (0 <= days_rem <= 30):
            recipient_id = c.assigned_to or c.created_by
            if recipient_id:
                existing = db.query(Notification).filter(
                    Notification.contract_id == c.id,
                    Notification.notification_type == "Renewal Reminder",
                    Notification.user_id == recipient_id,
                    Notification.created_at >= datetime.combine(today, datetime.min.time())
                ).first()

                if not existing:
                    notif = create_notification(
                        db=db,
                        user_id=recipient_id,
                        notification_type="Renewal Reminder",
                        title="Contract Renewal Approaching",
                        message=f"Contract '{c.title}' ({c.contract_number}) expires in {days_rem} days on {c.end_date}.",
                        contract_id=c.id
                    )
                    created_notifications.append(notif)

    return created_notifications


def generate_obligation_alerts(db: Session) -> List[Notification]:
    """
    Scans obligations and creates Obligation Due Alerts (within 7 days) and Obligation Overdue Alerts.
    """
    today = date.today()
    obligations = db.query(Obligation).all()
    created_notifications = []

    for ob in obligations:
        if not ob.due_date:
            continue

        days_until_due = (ob.due_date - today).days
        recipient_id = getattr(ob, "responsible_user_id", None) or getattr(ob, "assigned_to", None)

        if not recipient_id:
            contract_obj = db.query(Contract).filter(Contract.id == ob.contract_id).first()
            if contract_obj:
                recipient_id = contract_obj.assigned_to or contract_obj.created_by


        # 1. Overdue Alert
        if (ob.status == "Overdue" or (ob.due_date < today and ob.status != "Completed")) and recipient_id:
            existing = db.query(Notification).filter(
                Notification.obligation_id == ob.obligation_id,
                Notification.notification_type == "Obligation Overdue Alert",
                Notification.user_id == recipient_id,
                Notification.created_at >= datetime.combine(today, datetime.min.time())
            ).first()

            if not existing:
                notif = create_notification(
                    db=db,
                    user_id=recipient_id,
                    notification_type="Obligation Overdue Alert",
                    title="Obligation Overdue",
                    message=f"Obligation '{ob.title}' for contract #{ob.contract_id} was due on {ob.due_date} and is overdue.",
                    contract_id=ob.contract_id,
                    obligation_id=ob.obligation_id
                )
                created_notifications.append(notif)

        # 2. Due Soon Alert (within 7 days)
        elif 0 <= days_until_due <= 7 and ob.status != "Completed" and recipient_id:
            existing = db.query(Notification).filter(
                Notification.obligation_id == ob.obligation_id,
                Notification.notification_type == "Obligation Due Alert",
                Notification.user_id == recipient_id,
                Notification.created_at >= datetime.combine(today, datetime.min.time())
            ).first()

            if not existing:
                notif = create_notification(
                    db=db,
                    user_id=recipient_id,
                    notification_type="Obligation Due Alert",
                    title="Obligation Due Soon",
                    message=f"Obligation '{ob.title}' for contract #{ob.contract_id} is due in {days_until_due} days on {ob.due_date}.",
                    contract_id=ob.contract_id,
                    obligation_id=ob.obligation_id
                )
                created_notifications.append(notif)

    return created_notifications


def generate_compliance_alerts(db: Session) -> List[Notification]:
    """
    Scans contracts with overdue obligations and generates Compliance Alerts.
    """
    today = date.today()
    overdue_obs = db.query(Obligation).filter(
        (Obligation.status == "Overdue") | (Obligation.due_date < today)
    ).all()

    contract_ids_with_overdue = {ob.contract_id for ob in overdue_obs if ob.status != "Completed"}
    created_notifications = []

    for cid in contract_ids_with_overdue:
        c = db.query(Contract).filter(Contract.id == cid).first()
        if not c:
            continue
        rec = compliance_service.evaluate_contract_compliance(c.id, db)
        if rec.compliance_status in ["Non-Compliant", "High Risk"] or rec.risk_level == "High":
            recipient_id = c.assigned_to or c.created_by
            if recipient_id:
                existing = db.query(Notification).filter(
                    Notification.contract_id == c.id,
                    Notification.notification_type == "Compliance Alert",
                    Notification.user_id == recipient_id,
                    Notification.created_at >= datetime.combine(today, datetime.min.time())
                ).first()

                if not existing:
                    notif = create_notification(
                        db=db,
                        user_id=recipient_id,
                        notification_type="Compliance Alert",
                        title=f"{rec.compliance_status} Contract Detected",
                        message=f"Contract '{c.title}' ({c.contract_number}) has compliance status '{rec.compliance_status}' with {rec.overdue_obligations} overdue obligations.",
                        contract_id=c.id
                    )
                    created_notifications.append(notif)

    return created_notifications

