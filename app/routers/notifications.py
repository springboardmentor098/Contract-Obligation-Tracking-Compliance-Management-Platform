from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.notification import Notification
from app.models.user import User
from app.models.contract import Contract
from app.models.obligation import Obligation
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# =========================
# GET USER NOTIFICATIONS
# =========================

@router.get(
    "",
    response_model=list[NotificationResponse],
    status_code=status.HTTP_200_OK
)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user["user_id"]
    ).all()

    return notifications


# =========================
# GET NOTIFICATION BY ID
# =========================

@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK
)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    if notification.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this notification"
        )

    return notification


# =========================
# CREATE NOTIFICATION
# =========================

@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user = db.query(User).filter(
        User.id == notification_data.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if notification_data.contract_id is not None:
        contract = db.query(Contract).filter(
            Contract.id == notification_data.contract_id
        ).first()

        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found"
            )

    if notification_data.obligation_id is not None:
        obligation = db.query(Obligation).filter(
            Obligation.id == notification_data.obligation_id
        ).first()

        if not obligation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Obligation not found"
            )

    notification = Notification(
        user_id=notification_data.user_id,
        contract_id=notification_data.contract_id,
        obligation_id=notification_data.obligation_id,
        notification_type=notification_data.notification_type,
        title=notification_data.title,
        message=notification_data.message,
        status="Unread"
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


# =========================
# MARK NOTIFICATION AS READ
# =========================

@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    if notification.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this notification"
        )

    notification.status = "Read"
    notification.read_at = datetime.utcnow()

    db.commit()
    db.refresh(notification)

    return notification


# =========================
# MARK ALL NOTIFICATIONS AS READ
# =========================

@router.patch(
    "/read-all",
    status_code=status.HTTP_200_OK
)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user["user_id"],
        Notification.status == "Unread"
    ).all()

    current_time = datetime.utcnow()

    for notification in notifications:
        notification.status = "Read"
        notification.read_at = current_time

    db.commit()

    return {
        "message": "All notifications marked as read",
        "count": len(notifications)
    }