from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse
)
from app.routers.dependencies import get_current_user


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# ============================================================
# GET ALL MY NOTIFICATIONS
# ============================================================
@router.get(
    "",
    response_model=list[NotificationResponse]
)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(
        Notification.created_at.desc()
    ).all()


# ============================================================
# GET NOTIFICATION BY ID
# ============================================================
@router.get(
    "/{notification_id}",
    response_model=NotificationResponse
)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if notification is None:
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


# ============================================================
# CREATE NOTIFICATION
# ============================================================
@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if notification_data.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create notifications for yourself"
        )

    notification = Notification(
        user_id=current_user.id,
        contract_id=notification_data.contract_id,
        obligation_id=notification_data.obligation_id,
        notification_type=notification_data.notification_type,
        title=notification_data.title,
        message=notification_data.message,
        status="Unread",
        scheduled_at=notification_data.scheduled_at,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


# ============================================================
# MARK NOTIFICATION AS READ
# ============================================================
@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this notification"
        )

    notification.status = "Read"
    notification.read_at = datetime.now(timezone.utc)
    notification.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(notification)

    return notification


# ============================================================
# MARK ALL MY NOTIFICATIONS AS READ
# ============================================================
@router.patch(
    "/read-all",
    response_model=dict
)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.status == "Unread"
    ).all()

    current_time = datetime.now(timezone.utc)

    for notification in notifications:
        notification.status = "Read"
        notification.read_at = current_time
        notification.updated_at = current_time

    db.commit()

    return {
        "message": "All notifications marked as read",
        "updated_count": len(notifications)
    }