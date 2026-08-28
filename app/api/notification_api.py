from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.notification import Notification
from app.schemas.notification_schema import (
    NotificationCreate,
    NotificationResponse
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db)
):
    notification = Notification(
        user_id=notification_data.user_id,
        contract_id=notification_data.contract_id,
        message=notification_data.message,
        notification_type=notification_data.notification_type,
        is_read=notification_data.is_read
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


@router.get(
    "/",
    response_model=list[NotificationResponse]
)
def get_notifications(
    db: Session = Depends(get_db)
):
    return db.query(Notification).all()


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse
)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return notification