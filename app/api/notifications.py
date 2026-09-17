from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationStatusUpdate
)
from app.services.notification_service import create_notification
from app.core.dependencies import get_current_user


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
            detail="You can only create notifications for yourself"
        )

    notification = create_notification(
        db=db,
        user_id=notification_data.user_id,
        notification_type=notification_data.notification_type,
        title=notification_data.title,
        message=notification_data.message,
        contract_id=notification_data.contract_id,
        obligation_id=notification_data.obligation_id,
        scheduled_at=notification_data.scheduled_at
    )

    return notification


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationStatusUpdate
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
            detail="You do not have permission to access this notification"
        )

    notification.status = "Read"
    notification.read_at = datetime.now()
    notification.updated_at = datetime.now()

    db.commit()
    db.refresh(notification)

    return notification


@router.patch(
    "/read-all",
    response_model=list[NotificationStatusUpdate]
)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id,
            Notification.status == "Unread"
        )
        .all()
    )

    current_time = datetime.now()

    for notification in notifications:
        notification.status = "Read"
        notification.read_at = current_time
        notification.updated_at = current_time

    db.commit()

    for notification in notifications:
        db.refresh(notification)

    return notifications