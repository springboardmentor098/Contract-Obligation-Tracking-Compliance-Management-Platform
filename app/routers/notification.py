# app/routers/notifications.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.notification import Notification
from app.schemas.notification import (
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
    data: NotificationCreate,
    db: Session = Depends(get_db)
):
    notification = Notification(**data.model_dump())

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


@router.get("", response_model=list[NotificationResponse])
def get_notifications(db: Session = Depends(get_db)):
    return db.query(Notification).all()


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail=f"Notification {notification_id} not found"
        )

    return notification


@router.put(
    "/{notification_id}",
    response_model=NotificationResponse
)
def update_notification(
    notification_id: int,
    data: NotificationCreate,
    db: Session = Depends(get_db)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail=f"Notification {notification_id} not found"
        )

    for key, value in data.model_dump().items():
        setattr(notification, key, value)

    db.commit()
    db.refresh(notification)

    return notification


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail=f"Notification {notification_id} not found"
        )

    db.delete(notification)
    db.commit()

    return {
        "message": f"Notification {notification_id} deleted successfully"
    }
