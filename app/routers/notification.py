# app/routers/notifications.py

from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.notification import Notification
from app.models.user import User

from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationReadResponse,
)

from app.services.notification_service import (
    create_notification as create_notification_service,
)

from app.core.security import get_current_user


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


# =========================================================
# 1. GET CURRENT USER NOTIFICATIONS
# =========================================================

@router.get(
    "",
    response_model=list[NotificationResponse],
)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get notifications belonging only to the authenticated user.
    """

    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id
        )
        .order_by(
            Notification.created_at.desc()
        )
        .all()
    )

    return notifications


# =========================================================
# 2. GET NOTIFICATION BY ID
# =========================================================

@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a single notification belonging to the
    authenticated user.
    """

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id
        )
        .first()
    )

    # -----------------------------------------------------
    # Notification does not exist
    # -----------------------------------------------------

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Notification {notification_id} not found"
            ),
        )

    # -----------------------------------------------------
    # Ownership check
    # -----------------------------------------------------

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to access "
                "this notification"
            ),
        )

    return notification


# =========================================================
# 3. CREATE NOTIFICATION
# =========================================================

@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_notification(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a notification.

    For security, ordinary users cannot create a
    notification for another user.
    """

    # -----------------------------------------------------
    # Check target user
    # -----------------------------------------------------

    target_user = (
        db.query(User)
        .filter(
            User.id == data.user_id
        )
        .first()
    )

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"User {data.user_id} not found"
            ),
        )

    # -----------------------------------------------------
    # Authorization
    #
    # User can create notification for themselves.
    #
    # Administrator can create notification for
    # another user.
    # -----------------------------------------------------

    if (
        data.user_id != current_user.id
        and current_user.role != "Administrator"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You cannot create a notification "
                "for another user"
            ),
        )

    # -----------------------------------------------------
    # Create notification
    # -----------------------------------------------------

    try:

        notification = create_notification_service(
            db=db,
            user_id=data.user_id,
            contract_id=data.contract_id,
            obligation_id=data.obligation_id,
            notification_type=data.notification_type,
            title=data.title,
            message=data.message,
            scheduled_at=data.scheduled_at,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return notification


# =========================================================
# 4. MARK NOTIFICATION AS READ
# =========================================================

@router.patch(
    "/{notification_id}/read",
    response_model=NotificationReadResponse,
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a notification belonging to the authenticated
    user as Read.
    """

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id
        )
        .first()
    )

    # -----------------------------------------------------
    # Notification does not exist
    # -----------------------------------------------------

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Notification {notification_id} not found"
            ),
        )

    # -----------------------------------------------------
    # Ownership check
    # -----------------------------------------------------

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to modify "
                "this notification"
            ),
        )

    # -----------------------------------------------------
    # Mark as read
    # -----------------------------------------------------

    now = datetime.now(timezone.utc)

    notification.status = "Read"

    notification.read_at = now

    notification.updated_at = now

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    db.commit()

    db.refresh(notification)

    return notification


# =========================================================
# 5. MARK ALL NOTIFICATIONS AS READ
# =========================================================

@router.patch(
    "/read-all",
)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark all unread notifications belonging to the
    authenticated user as Read.
    """

    # -----------------------------------------------------
    # Find only current user's unread notifications
    # -----------------------------------------------------

    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id,
            Notification.status == "Unread",
        )
        .all()
    )

    # -----------------------------------------------------
    # Current timestamp
    # -----------------------------------------------------

    now = datetime.now(timezone.utc)

    # -----------------------------------------------------
    # Mark all as read
    # -----------------------------------------------------

    for notification in notifications:

        notification.status = "Read"

        notification.read_at = now

        notification.updated_at = now

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    db.commit()

    return {
        "message": (
            "All unread notifications marked as read"
        ),
        "updated_count": len(notifications),
    }