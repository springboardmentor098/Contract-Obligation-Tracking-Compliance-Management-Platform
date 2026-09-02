import os
import smtplib
from email.message import EmailMessage
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.all_models import (
    Notification, 
    NotificationTypeEnum, 
    NotificationStatusEnum, 
    User
)

#  Background Email Function
def send_email_alert(to_email: str, subject: str, body: str):
    host = os.environ.get("SMTP_HOST")
    port = os.environ.get("SMTP_PORT", 587)
    username = os.environ.get("SMTP_USERNAME")
    password = os.environ.get("SMTP_PASSWORD")

    # Only attempt to send if credentials exist in the .env file
    if not all([host, username, password]):
        print(" SMTP credentials missing. Skipping email notification.")
        return

    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = username
        msg['To'] = to_email

        server = smtplib.SMTP(host, int(port))
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        print(f" Email sent successfully to {to_email}")
    except Exception as e:
        print(f" Failed to send email: {e}")
        # We catch the exception so the main API doesn't crash!

#  Core Notification Creator
def create_notification(
    db: Session, 
    user_id: int, 
    title: str, 
    message: str, 
    notif_type: NotificationTypeEnum, 
    contract_id: int = None, 
    obligation_id: int = None
):
    # 1. Save to Database
    new_notif = Notification(
        user_id=user_id,
        contract_id=contract_id,
        obligation_id=obligation_id,
        notification_type=notif_type,
        title=title,
        message=message,
        status=NotificationStatusEnum.UNREAD
    )
    db.add(new_notif)
    db.commit()
    db.refresh(new_notif)

    # 2. Try sending the email to the user
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.email:
        send_email_alert(user.email, title, message)
        
        # Mark as sent in DB
        new_notif.sent_at = datetime.utcnow()
        db.commit()

    return new_notif

# ==========================================
#  AUTOMATED EVENT TRIGGERS
# ==========================================

def trigger_renewal_reminder(db: Session, user_id: int, contract_id: int, days_left: int, contract_title: str):
    title = "Contract Renewal Approaching"
    message = f"The contract '{contract_title}' expires in {days_left} days. Please review it for renewal."
    return create_notification(db, user_id, title, message, NotificationTypeEnum.RENEWAL_REMINDER, contract_id=contract_id)

def trigger_obligation_overdue(db: Session, user_id: int, contract_id: int, obligation_id: int, obligation_title: str):
    title = "🚨 Obligation Overdue Alert"
    message = f"The obligation '{obligation_title}' has passed its due date and is now Overdue. Immediate action is required."
    return create_notification(db, user_id, title, message, NotificationTypeEnum.OBLIGATION_OVERDUE, contract_id=contract_id, obligation_id=obligation_id)

def trigger_compliance_alert(db: Session, user_id: int, contract_id: int, contract_title: str):
    title = "⚠️ High-Risk Contract Detected"
    message = f"Contract '{contract_title}' has multiple overdue obligations and has been marked as High Risk."
    return create_notification(db, user_id, title, message, NotificationTypeEnum.COMPLIANCE_ALERT, contract_id=contract_id)