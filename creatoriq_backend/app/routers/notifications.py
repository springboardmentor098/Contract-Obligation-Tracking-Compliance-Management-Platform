from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationListResponse,
    NotificationResponse,
)
from app.services.notification_service import (
    create_notification,
    get_notification_by_id,
    get_user_notifications,
    mark_all_notifications_as_read,
    mark_notification_as_read,
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# ============================================================
# 1. GET USER NOTIFICATIONS
# GET /notifications
# ============================================================

@router.get(
    "",
    response_model=list[NotificationListResponse],
    status_code=status.HTTP_200_OK,
)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_notifications(
        db,
        current_user.id
    )


# ============================================================
# 2. CREATE NOTIFICATION
# POST /notifications
# ============================================================

@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_notification_api(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Notification belongs to authenticated user.
    notification_data.user_id = current_user.id

    return create_notification(
        db,
        notification_data
    )


# ============================================================
# 3. MARK ALL NOTIFICATIONS AS READ
# PATCH /notifications/read-all
# ============================================================

@router.patch(
    "/read-all",
    status_code=status.HTTP_200_OK,
)
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return mark_all_notifications_as_read(
        db,
        current_user.id
    )


# ============================================================
# 4. GET NOTIFICATION BY ID
# GET /notifications/{notification_id}
# ============================================================

@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_notification_by_id(
        db,
        notification_id,
        current_user.id
    )


# ============================================================
# 5. MARK ONE NOTIFICATION AS READ
# PATCH /notifications/{notification_id}/read
# ============================================================

@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return mark_notification_as_read(
        db,
        notification_id,
        current_user.id
    )