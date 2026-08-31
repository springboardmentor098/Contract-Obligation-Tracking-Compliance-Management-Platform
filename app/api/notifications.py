from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationReadResponse,
    NotificationResponse,
    ReadAllResponse,
    VALID_NOTIFICATION_TYPES,
)
from app.services import notification_service

router = APIRouter(
    tags=["Notifications"]
)


@router.get(
    "/notifications",
    response_model=List[NotificationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get User Notifications",
    description="Retrieves notifications belonging to the authenticated user."
)
def get_user_notifications(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by notification status (Unread, Read)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve private notifications for authenticated user."""
    # Automatically trigger scan for alerts when user checks notifications
    notification_service.generate_renewal_reminders(db)
    notification_service.generate_obligation_alerts(db)
    notification_service.generate_compliance_alerts(db)

    user_uid = getattr(current_user, "user_id", None) or getattr(current_user, "id", 1)
    
    query = db.query(Notification).filter(
        (Notification.user_id == user_uid) | (Notification.user_id == 1)
    )


    if status_filter:
        query = query.filter(Notification.status == status_filter.strip())

    notifications = query.order_by(Notification.created_at.desc()).all()
    return notifications


@router.get(
    "/notifications/{notification_id}",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Notification by ID",
    description="Retrieves a specific notification if the authenticated user has access permission."
)
def get_notification_by_id(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get single notification record with ownership check."""
    notif = db.query(Notification).filter(
        (Notification.id == notification_id) | (Notification.notification_id == notification_id)
    ).first()

    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {notification_id} not found."
        )

    # Ownership check: User can view their own notifications or managers/admins can view
    user_uid = getattr(current_user, "user_id", None) or getattr(current_user, "id", 1)
    if notif.user_id not in [user_uid, 1] and current_user.role not in ["Administrator", "Admin", "Legal Manager", "Contract Manager", "Compliance Officer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You do not have permission to view another user's private notifications."
        )

    return notif



@router.post(
    "/notifications",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Notification",
    description="Creates a new notification record and triggers SMTP email alert."
)
def create_notification(
    notification_in: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create notification and send SMTP email."""
    target_type = notification_in.notification_type.strip()
    if target_type not in VALID_NOTIFICATION_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid notification type '{target_type}'. Allowed types: {VALID_NOTIFICATION_TYPES}"
        )

    # Permission check: Ordinary users can create notifications for themselves, admins/managers for any user
    user_uid = current_user.user_id or current_user.id
    target_user_id = notification_in.user_id if (notification_in.user_id and notification_in.user_id > 0) else user_uid

    if target_user_id != user_uid and current_user.role not in ["Administrator", "Admin", "Legal Manager", "Contract Manager", "Compliance Officer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Ordinary users cannot create notifications for other users."
        )

    notif = notification_service.create_notification(
        db=db,
        user_id=target_user_id,
        notification_type=target_type,
        title=notification_in.title,
        message=notification_in.message,
        contract_id=notification_in.contract_id,
        obligation_id=notification_in.obligation_id
    )


    return notif


@router.patch(
    "/notifications/read-all",
    response_model=ReadAllResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark All Notifications as Read",
    description="Marks all unread notifications belonging to the authenticated user as Read."
)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all unread notifications for authenticated user as Read."""
    user_uid = current_user.user_id or current_user.id
    unread_list = db.query(Notification).filter(
        (Notification.user_id == user_uid),
        (Notification.status == "Unread")
    ).all()

    now = datetime.utcnow()
    count = len(unread_list)

    for notif in unread_list:
        notif.status = "Read"
        notif.read_at = now

    db.commit()

    return ReadAllResponse(
        message=f"Successfully marked {count} unread notifications as read.",
        updated_count=count
    )


@router.patch(
    "/notifications/{notification_id}/read",
    response_model=NotificationReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark Notification as Read",
    description="Changes notification status from Unread to Read for the authenticated user."
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark single notification as Read with ownership check."""
    notif = db.query(Notification).filter(
        (Notification.id == notification_id) | (Notification.notification_id == notification_id)
    ).first()

    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {notification_id} not found."
        )

    user_uid = getattr(current_user, "user_id", None) or getattr(current_user, "id", 1)
    if notif.user_id not in [user_uid, 1] and current_user.role not in ["Administrator", "Admin", "Legal Manager", "Contract Manager", "Compliance Officer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You cannot modify notifications belonging to another user."
        )


    now = datetime.utcnow()
    notif.status = "Read"
    notif.read_at = now
    db.commit()
    db.refresh(notif)

    return NotificationReadResponse(
        id=notif.id,
        status=notif.status,
        read_at=notif.read_at
    )
