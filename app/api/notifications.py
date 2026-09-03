from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.notification import Notification
from app.schemas.notification_schema import (
    NotificationCreate,
    NotificationResponse,
)
from app.services.notification_service import (
    create_notification,
    mark_notification_as_read,
    mark_all_notifications_as_read,
)
from app.middleware.auth import require_roles


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# ============================================================
# AUTHORIZED ROLES
# ============================================================

VIEW_ROLES = (
    "Administrator",
    "Legal Manager",
    "Compliance Officer",
    "Contract Manager",
    "Department Head",
    "Employee",
)

CREATE_ROLES = (
    "Administrator",
    "Legal Manager",
    "Compliance Officer",
    "Contract Manager",
)


# ============================================================
# GET USER NOTIFICATIONS
# ============================================================

@router.get(
    "",
    response_model=list[NotificationResponse],
    status_code=status.HTTP_200_OK,
)
def get_notifications(
    current_user: dict = Depends(
        require_roles(*VIEW_ROLES)
    ),
    db: Session = Depends(get_db)
):

    user_id = int(current_user["user_id"])

    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id
        )
        .order_by(
            Notification.created_at.desc()
        )
        .all()
    )

    return notifications


# ============================================================
# GET NOTIFICATION BY ID
# ============================================================

@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
)
def get_notification(
    notification_id: int,
    current_user: dict = Depends(
        require_roles(*VIEW_ROLES)
    ),
    db: Session = Depends(get_db)
):

    user_id = int(current_user["user_id"])

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    # --------------------------------------------------------
    # Ownership check
    # --------------------------------------------------------

    if notification.user_id != user_id:
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
    status_code=status.HTTP_201_CREATED,
)
def create_new_notification(
    notification_data: NotificationCreate,
    current_user: dict = Depends(
        require_roles(*CREATE_ROLES)
    ),
    db: Session = Depends(get_db)
):

    notification = create_notification(
        db=db,
        user_id=notification_data.user_id,
        contract_id=notification_data.contract_id,
        obligation_id=notification_data.obligation_id,
        notification_type=notification_data.notification_type,
        title=notification_data.title,
        message=notification_data.message,
        scheduled_at=notification_data.scheduled_at,
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return notification


# ============================================================
# MARK NOTIFICATION AS READ
# ============================================================

@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
)
def mark_as_read(
    notification_id: int,
    current_user: dict = Depends(
        require_roles(*VIEW_ROLES)
    ),
    db: Session = Depends(get_db)
):

    user_id = int(current_user["user_id"])

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    # --------------------------------------------------------
    # Ownership check
    # --------------------------------------------------------

    if notification.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this notification"
        )

    return mark_notification_as_read(
        db,
        notification
    )


# ============================================================
# MARK ALL NOTIFICATIONS AS READ
# ============================================================

@router.patch(
    "/read-all",
    status_code=status.HTTP_200_OK,
)
def mark_all_as_read(
    current_user: dict = Depends(
        require_roles(*VIEW_ROLES)
    ),
    db: Session = Depends(get_db)
):

    user_id = int(current_user["user_id"])

    count = mark_all_notifications_as_read(
        db,
        user_id
    )

    return {
        "message": "All notifications marked as read",
        "updated_count": count
    }