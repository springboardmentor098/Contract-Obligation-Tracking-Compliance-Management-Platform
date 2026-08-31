from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.models.contract import Contract
from app.models.obligation import Obligation
from app.schemas.notification_schema import (
    NotificationCreate,
    NotificationUpdate,
    NotificationStatusUpdate,
    NotificationResponse,
)
from app.core.auth import get_current_user


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


# ---------------- CREATE ----------------

@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_notification(
    notification_data: NotificationCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.id == notification_data.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if notification_data.contract_id:
        contract = db.query(Contract).filter(
            Contract.id == notification_data.contract_id
        ).first()

        if not contract:
            raise HTTPException(
                status_code=404,
                detail="Contract not found",
            )

    if notification_data.obligation_id:
        obligation = db.query(Obligation).filter(
            Obligation.id == notification_data.obligation_id
        ).first()

        if not obligation:
            raise HTTPException(
                status_code=404,
                detail="Obligation not found",
            )

    notification = Notification(**notification_data.model_dump())

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


# ---------------- GET ALL ----------------

@router.get(
    "/",
    response_model=list[NotificationResponse],
)
def get_notifications(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Notification).all()


# ---------------- GET ONE ----------------

@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def get_notification(
    notification_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    return notification


# ---------------- UPDATE ----------------

@router.put(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def update_notification(
    notification_id: int,
    notification_data: NotificationUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    update_data = notification_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(notification, key, value)

    db.commit()
    db.refresh(notification)

    return notification


# ---------------- MARK AS READ ----------------

@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_as_read(
    notification_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    notification.status = "Read"
    notification.read_at = datetime.utcnow()

    db.commit()
    db.refresh(notification)

    return notification


# ---------------- DELETE ----------------

@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_notification(
    notification_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found",
        )

    db.delete(notification)
    db.commit()