from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationService:

    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        title: str,
        message: str,
        notification_type: str,
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
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        return notification

    @staticmethod
    def create_renewal_reminder(
        db: Session,
        user_id: int,
        contract_id: int,
        message: str
    ):
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            contract_id=contract_id,
            notification_type="Renewal Reminder",
            title="Contract Renewal Approaching",
            message=message
        )

    @staticmethod
    def create_obligation_due_alert(
        db: Session,
        user_id: int,
        contract_id: int,
        obligation_id: int,
        message: str
    ):
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            contract_id=contract_id,
            obligation_id=obligation_id,
            notification_type="Obligation Due Alert",
            title="Obligation Due Soon",
            message=message
        )

    @staticmethod
    def create_obligation_overdue_alert(
        db: Session,
        user_id: int,
        contract_id: int,
        obligation_id: int,
        message: str
    ):
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            contract_id=contract_id,
            obligation_id=obligation_id,
            notification_type="Obligation Overdue Alert",
            title="Obligation Overdue",
            message=message
        )

    @staticmethod
    def create_compliance_alert(
        db: Session,
        user_id: int,
        contract_id: int,
        message: str
    ):
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            contract_id=contract_id,
            notification_type="Compliance Alert",
            title="Compliance Issue Detected",
            message=message
        )

    @staticmethod
    def create_approval_notification(
        db: Session,
        user_id: int,
        contract_id: int,
        message: str
    ):
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            contract_id=contract_id,
            notification_type="Contract Approval Alert",
            title="Contract Approval Notification",
            message=message
        )