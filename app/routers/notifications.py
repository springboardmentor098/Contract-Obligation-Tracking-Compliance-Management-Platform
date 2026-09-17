from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services.notification_service import generate_obligation_alerts
from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse
)
from app.services.notification_service import generate_compliance_alert
from app.models.contract import Contract
from app.services.notification_service import create_notification
from app.services.notification_service import (
    generate_obligation_alerts,
    generate_renewal_reminders
)

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get(
    "",
    response_model=list[NotificationResponse]
)
def get_user_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    return notifications


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse
)
def get_notification_by_id(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this notification"
        )

    return notification


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if notification_data.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot create a notification for another user"
        )

    return create_notification(
        db=db,
        user_id=notification_data.user_id,
        contract_id=notification_data.contract_id,
        obligation_id=notification_data.obligation_id,
        notification_type=notification_data.notification_type,
        title=notification_data.title,
        message=notification_data.message,
        scheduled_at=notification_data.scheduled_at
    )
    @router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse
)
    def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
      notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this notification"
        )

    notification.status = "Read"
    notification.read_at = datetime.now()
    notification.updated_at = datetime.now()

    db.commit()
    db.refresh(notification)

    return notification


@router.patch("/read-all")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    unread_notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id,
            Notification.status == "Unread"
        )
        .all()
    )

    current_time = datetime.now()

    for notification in unread_notifications:
        notification.status = "Read"
        notification.read_at = current_time
        notification.updated_at = current_time

    db.commit()

    return {
        "message": "All notifications marked as read"
    }
@router.patch("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this notification"
        )

    notification.status = "Read"
    notification.read_at = datetime.now()

    db.commit()
    db.refresh(notification)

    return notification
@router.post("/generate-obligation-alerts")
def test_generate_obligation_alerts(
    db: Session = Depends(get_db)
):
    notifications = generate_obligation_alerts(db)

    return {
        "message": "Obligation alerts generated successfully",
        "notifications_created": len(notifications)
    }
@router.post("/generate-renewal-reminders")
def test_generate_renewal_reminders(
    db: Session = Depends(get_db)
):
    notifications = generate_renewal_reminders(db)

    return {
        "message": "Renewal reminders generated successfully",
        "notifications_created": len(notifications)
    }
@router.post("/generate-compliance-alert/{contract_id}")
def test_generate_compliance_alert(
    contract_id: int,
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        return {
            "message": "Contract not found"
        }

    notification = generate_compliance_alert(
        db=db,
        contract=contract,
        compliance_status="Non-Compliant",
        risk_level="Medium"
    )

    if not notification:
        return {
            "message": "Compliance alert was not generated"
        }

    return {
        "message": "Compliance alert generated successfully",
        "notification_id": notification.id
    }