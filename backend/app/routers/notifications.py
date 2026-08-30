from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
)
from app.services.notification_service import (
    create_notification,
    delete_notification,
    get_notification,
    get_unread_notifications,
    get_user_notifications,
    mark_all_notifications_as_read,
    mark_notification_as_read,
    mark_notification_as_unread,
)

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a notification for the logged-in user.
    """

    return create_notification(
        db=db,
        user_id=current_user.id,
        notification_type=notification_data.notification_type,
        title=notification_data.title,
        message=notification_data.message,
        contract_id=notification_data.contract_id,
        obligation_id=notification_data.obligation_id,
        scheduled_at=notification_data.scheduled_at,
        status=notification_data.status or "Pending",
    )


@router.get(
    "",
    response_model=list[NotificationResponse],
)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return all notifications for the logged-in user.
    """

    return get_user_notifications(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/unread",
    response_model=list[NotificationResponse],
)
def get_unread(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return unread notifications for the logged-in user.
    """

    return get_unread_notifications(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def get_single_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return one notification belonging to the logged-in user.
    """

    notification = get_notification(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id,
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return notification


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a notification as read.
    """

    notification = get_notification(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id,
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return mark_notification_as_read(
        db=db,
        notification=notification,
    )


@router.patch(
    "/{notification_id}/unread",
    response_model=NotificationResponse,
)
def mark_unread(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark a notification as unread.
    """

    notification = get_notification(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id,
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return mark_notification_as_unread(
        db=db,
        notification=notification,
    )


@router.patch(
    "/read-all",
)
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mark all notifications for the logged-in user as read.
    """

    count = mark_all_notifications_as_read(
        db=db,
        user_id=current_user.id,
    )

    return {
        "message": "All notifications marked as read",
        "updated_count": count,
    }


@router.delete(
    "/{notification_id}",
)
def delete_single_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a notification belonging to the logged-in user.
    """

    notification = get_notification(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id,
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    delete_notification(
        db=db,
        notification=notification,
    )

    return {
        "message": "Notification deleted successfully",
    }