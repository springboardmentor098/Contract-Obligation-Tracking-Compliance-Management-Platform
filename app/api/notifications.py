from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.models.contract import Contract
from app.schemas.notification_schema import (
    NotificationCreate,
    NotificationUpdate,
    NotificationRead,
)
from app.services.audit_service import create_audit_log
from app.core.dependencies import get_current_user, require_permission
from app.core.permissions import Permission


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


# =========================================================
# CREATE NOTIFICATION
# =========================================================

@router.post(
    "",
    response_model=NotificationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.MANAGE_USERS)
    ),
):
    user = (
        db.query(User)
        .filter(User.id == notification_data.user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create notification for inactive user",
        )

    if notification_data.contract_id is not None:
        contract = (
            db.query(Contract)
            .filter(Contract.id == notification_data.contract_id)
            .first()
        )

        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found",
            )

    notification = Notification(
        user_id=notification_data.user_id,
        contract_id=notification_data.contract_id,
        title=notification_data.title,
        message=notification_data.message,
        notification_type=notification_data.notification_type,
        is_read=False,
    )

    db.add(notification)
    db.flush()

    create_audit_log(
        db=db,
        user_id=int(current_user["sub"]),
        contract_id=notification.contract_id,
        action="Created notification",
        entity_type="Notification",
        entity_id=notification.id,
        details=(
            f"Created notification '{notification.title}' "
            f"for user ID {notification.user_id}"
        ),
    )

    db.commit()
    db.refresh(notification)

    return notification


# =========================================================
# LIST CURRENT USER NOTIFICATIONS
# =========================================================

@router.get(
    "",
    response_model=list[NotificationRead],
)
def list_notifications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])

    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )


# =========================================================
# GET CURRENT USER NOTIFICATION
# =========================================================

@router.get(
    "/{notification_id}",
    response_model=NotificationRead,
)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return notification


# =========================================================
# MARK NOTIFICATION READ / UNREAD
# =========================================================

@router.patch(
    "/{notification_id}",
    response_model=NotificationRead,
)
def update_notification(
    notification_id: int,
    notification_data: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    old_status = notification.is_read
    notification.is_read = notification_data.is_read

    create_audit_log(
        db=db,
        user_id=user_id,
        contract_id=notification.contract_id,
        action="Updated notification",
        entity_type="Notification",
        entity_id=notification.id,
        details=(
            f"is_read: {old_status} -> "
            f"{notification.is_read}"
        ),
    )

    db.commit()
    db.refresh(notification)

    return notification


# =========================================================
# DELETE NOTIFICATION
# =========================================================

@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.MANAGE_USERS)
    ),
):
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id)
        .first()
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    contract_id = notification.contract_id
    title = notification.title
    user_id = notification.user_id

    create_audit_log(
        db=db,
        user_id=int(current_user["sub"]),
        contract_id=contract_id,
        action="Deleted notification",
        entity_type="Notification",
        entity_id=notification.id,
        details=(
            f"Deleted notification '{title}' "
            f"for user ID {user_id}"
        ),
    )

    db.delete(notification)
    db.commit()

    return None
