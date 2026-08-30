from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.notification import Notification
from backend.app.models.user import User
from backend.app.models.contract import Contract
from backend.app.models.obligation import Obligation
from backend.app.core.auth import get_current_user

from backend.app.schemas.notification import (
    NotificationCreate,
    NotificationOut
)
from backend.app.services.notification_service import check_renewal_reminders
from backend.app.services.notification_service import check_obligation_due_reminders
from backend.app.services.notification_service import check_compliance_alerts
from backend.app.services.notification_service import create_notification as create_notification_service

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# ============================================================
# GET USER NOTIFICATIONS
# ============================================================

@router.get(
    "",
    response_model=list[NotificationOut]
)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user = db.query(User).filter(
        User.email == current_user["email"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    notifications = db.query(Notification).filter(
        Notification.user_id == user.id
    ).order_by(
        Notification.created_at.desc()
    ).all()

    return notifications
# ============================================================
# CHECK RENEWAL REMINDERS
# ============================================================

@router.post(
    "/renewal-reminders"
)
def trigger_renewal_reminders(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrator can trigger renewal reminders"
        )

    notifications = check_renewal_reminders(db)

    return {
        "message": "Renewal reminders processed successfully",
        "created_count": len(notifications)
    }


# ============================================================
# GET NOTIFICATION BY ID
# ============================================================

@router.get(
    "/{notification_id}",
    response_model=NotificationOut
)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user = db.query(User).filter(
        User.email == current_user["email"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    # Ownership check
    if notification.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this notification"
        )

    return notification


# ============================================================
# CREATE NOTIFICATION
# ============================================================

@router.post(
    "",
    response_model=NotificationOut,
    status_code=status.HTTP_201_CREATED
)
def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    # Check target user
    user = db.query(User).filter(
        User.id == notification_data.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check contract if provided
    if notification_data.contract_id is not None:
        contract = db.query(Contract).filter(
            Contract.id == notification_data.contract_id
        ).first()

        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found"
            )

    # Check obligation if provided
    if notification_data.obligation_id is not None:
        obligation = db.query(Obligation).filter(
            Obligation.id == notification_data.obligation_id
        ).first()

        if not obligation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Obligation not found"
            )

    # Allowed notification types
    allowed_types = [
        "Renewal Reminder",
        "Obligation Due Alert",
        "Obligation Overdue Alert",
        "Compliance Alert",
        "Contract Approval Alert",
        "Contract Status Alert"
    ]

    if notification_data.notification_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification type"
        )
    new_notification = create_notification_service(
    db=db,
    user_id=notification_data.user_id,
    contract_id=notification_data.contract_id,
    obligation_id=notification_data.obligation_id,
    notification_type=notification_data.notification_type,
    title=notification_data.title,
    message=notification_data.message,
)
    return new_notification


# ============================================================
# MARK NOTIFICATION AS READ
# ============================================================

@router.patch(
    "/{notification_id}/read",
    response_model=NotificationOut
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user = db.query(User).filter(
        User.email == current_user["email"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    if notification.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this notification"
        )

    notification.status = "Read"
    notification.read_at = datetime.utcnow()
    notification.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(notification)

    return notification


# ============================================================
# MARK ALL NOTIFICATIONS AS READ
# ============================================================

@router.patch(
    "/read-all"
)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user = db.query(User).filter(
        User.email == current_user["email"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    notifications = db.query(Notification).filter(
        Notification.user_id == user.id,
        Notification.status == "Unread"
    ).all()

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
# CHECK OBLIGATION DUE REMINDERS
# ============================================================
@router.post(
    "/obligation-due-reminders"
)
def process_obligation_due_reminders(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrator can trigger obligation due reminders"
        )

    notifications = check_obligation_due_reminders(db)

    return {
        "message": "Obligation due reminders processed successfully",
        "created_count": len(notifications)
    }
# ============================================================
# CHECK COMPLIANCE ALERTS
# ============================================================

@router.post(
    "/compliance-alerts"
)
def process_compliance_alerts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != "Administrator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrator can trigger compliance alerts"
        )

    notifications = check_compliance_alerts(db)

    return {
        "message": "Compliance alerts processed successfully",
        "created_count": len(notifications)
    }