from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.notification import Notification
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationReadResponse,
)
from app.services.notification_service import (
    create_notification,
    mark_notification_read,
    mark_all_notifications_read,
    generate_renewal_reminders,
    generate_obligation_alerts,
)
from app.utils.authorization import get_current_user


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


def get_notification_or_404(
    notification_id: int,
    db: Session,
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return notification


def check_notification_owner(
    notification: Notification,
    current_user: dict,
):
    if notification.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this notification",
        )


@router.get(
    "",
    response_model=list[NotificationResponse],
)
def get_notifications(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Notification).filter(
        Notification.user_id == current_user["user_id"]
    ).order_by(
        Notification.created_at.desc()
    ).all()


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def get_notification(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = get_notification_or_404(
        notification_id,
        db,
    )

    check_notification_owner(
        notification,
        current_user,
    )

    return notification


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_notification_api(
    notification_data: NotificationCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (
        notification_data.user_id != current_user["user_id"]
        and current_user.get("role")
        not in {
            "Administrator",
            "Contract Manager",
            "Legal Manager",
        }
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot create notifications for another user",
        )

    return create_notification(
        db=db,
        user_id=notification_data.user_id,
        contract_id=notification_data.contract_id,
        obligation_id=notification_data.obligation_id,
        notification_type=notification_data.notification_type,
        title=notification_data.title,
        message=notification_data.message,
        scheduled_at=notification_data.scheduled_at,
    )


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationReadResponse,
)
def mark_as_read(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = get_notification_or_404(
        notification_id,
        db,
    )

    check_notification_owner(
        notification,
        current_user,
    )

    return mark_notification_read(
        notification,
        db,
    )


@router.patch(
    "/read-all",
)
def mark_all_as_read(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    count = mark_all_notifications_read(
        current_user["user_id"],
        db,
    )

    return {
        "message": "All notifications marked as read",
        "updated_count": count,
    }


@router.post(
    "/generate/renewal-reminders",
    response_model=list[NotificationResponse],
)
def generate_renewal_notifications(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.get("role") not in {
        "Administrator",
        "Contract Manager",
        "Legal Manager",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to generate reminders",
        )

    return generate_renewal_reminders(db)


@router.post(
    "/generate/obligation-alerts",
    response_model=list[NotificationResponse],
)
def generate_obligation_notifications(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.get("role") not in {
        "Administrator",
        "Contract Manager",
        "Legal Manager",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to generate alerts",
        )

    return generate_obligation_alerts(db)
