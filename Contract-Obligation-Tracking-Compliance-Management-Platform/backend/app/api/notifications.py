from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.security import get_current_user

from app.models.notification import Notification
from app.models.user import User

from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationReadResponse,
    MarkAllReadResponse,
)

from app.services.notification_service import (
    create_notification,
    mark_notification_as_read,
    mark_all_notifications_as_read,
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


# ============================================================
# GET /notifications
# ============================================================

@router.get(
    "",
    response_model=list[NotificationResponse],
)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id
        )
        .order_by(
            Notification.created_at.desc()
        )
        .all()
    )


# ============================================================
# GET /notifications/{notification_id}
# ============================================================

@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this notification",
        )

    return notification


# ============================================================
# POST /notifications
# ============================================================

@router.post(
    "",
    response_model=NotificationResponse,
    status_code=201,
)
def create_notification_api(
    data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # Ordinary users can only create notifications for themselves.
    # Managers/admins may create notifications for other users.
    role = getattr(current_user, "role", None)

    manager_roles = {
        "admin",
        "Admin",
        "manager",
        "Manager",
        "contract_manager",
        "Contract Manager",
    }

    if (
        data.user_id != current_user.id
        and role not in manager_roles
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "You are not authorized to create "
                "notifications for another user"
            ),
        )

    return create_notification(
        db,
        data,
    )


# ============================================================
# PATCH /notifications/{notification_id}/read
# ============================================================

@router.patch(
    "/{notification_id}/read",
    response_model=NotificationReadResponse,
)
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to modify this notification",
        )

    return mark_notification_as_read(
        db,
        notification,
    )


# ============================================================
# PATCH /notifications/read-all
# ============================================================

@router.patch(
    "/read-all",
    response_model=MarkAllReadResponse,
)
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    count = mark_all_notifications_as_read(
        db,
        current_user.id,
    )

    return {
        "message": "All unread notifications marked as read",
        "updated_count": count,
    }