from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.notification import Notification, NotificationStatus
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.core.deps import get_current_active_user
from app.services.email_service import send_email

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=List[NotificationResponse])
def get_my_notifications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    if notification.user_id != current_user.id and current_user.role != UserRole.ADMINISTRATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your notification")
    return notification


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    payload: NotificationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Ordinary users may only create notifications for themselves; only
    # managers/administrators may notify other users directly via this API.
    manager_roles = (
        UserRole.ADMINISTRATOR,
        UserRole.LEGAL_MANAGER,
        UserRole.CONTRACT_MANAGER,
        UserRole.COMPLIANCE_OFFICER,
    )
    if payload.user_id != current_user.id and current_user.role not in manager_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot create notifications for other users",
        )

    recipient = db.query(User).filter(User.id == payload.user_id).first()
    if not recipient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient user not found")

    notification = Notification(
        user_id=payload.user_id,
        contract_id=payload.contract_id,
        obligation_id=payload.obligation_id,
        notification_type=payload.notification_type,
        title=payload.title,
        message=payload.message,
        status=NotificationStatus.UNREAD,
        scheduled_at=payload.scheduled_at,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    if send_email(recipient.email, payload.title, payload.message):
        notification.sent_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(notification)

    return notification


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your notification")

    notification.status = NotificationStatus.READ
    notification.read_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(notification)
    return notification


@router.patch("/read-all", status_code=status.HTTP_200_OK)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    updated = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.status == NotificationStatus.UNREAD)
        .update(
            {
                Notification.status: NotificationStatus.READ,
                Notification.read_at: datetime.now(timezone.utc),
            }
        )
    )
    db.commit()
    return {"updated_count": updated}
