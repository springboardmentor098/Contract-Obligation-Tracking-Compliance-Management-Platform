# from datetime import datetime

# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session

# from app.database.database import get_db
# from app.models.notification import Notification
# from app.services.compliance_service import calculate_contract_compliance
# from app.models.user import User
# from app.schemas.notification import (
#     NotificationCreate,
#     NotificationResponse,
# )
# from app.core.dependencies import get_current_user
# from app.services.notification_service import (
#     create_notification,
#     generate_renewal_reminders,
#     generate_obligation_alerts,
# )

# router = APIRouter(
#     prefix="/notifications",
#     tags=["Notifications"]
# )


# @router.get(
#     "/",
#     response_model=list[NotificationResponse]
# )
# def get_notifications(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     return (
#         db.query(Notification)
#         .filter(Notification.user_id == current_user.id)
#         .order_by(Notification.created_at.desc())
#         .all()
#     )


# @router.get(
#     "/{notification_id}",
#     response_model=NotificationResponse
# )
# def get_notification(
#     notification_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     notification = (
#         db.query(Notification)
#         .filter(Notification.id == notification_id)
#         .first()
#     )

#     if notification is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Notification not found"
#         )

#     if notification.user_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You do not have permission to access this notification"
#         )

#     return notification


# @router.post(
#     "/",
#     response_model=NotificationResponse,
#     status_code=status.HTTP_201_CREATED
# )
# def create_user_notification(
#     notification_data: NotificationCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     if notification_data.user_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You cannot create notifications for another user"
#         )

#     try:
#         notification = create_notification(
#             db=db,
#             user_id=notification_data.user_id,
#             contract_id=notification_data.contract_id,
#             obligation_id=notification_data.obligation_id,
#             renewal_id=notification_data.renewal_id,
#             notification_type=notification_data.notification_type,
#             title=notification_data.title,
#             message=notification_data.message,
#         )
#     except ValueError as exc:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(exc)
#         )

#     return notification


# @router.patch(
#     "/{notification_id}/read",
#     response_model=NotificationResponse
# )
# def mark_notification_as_read(
#     notification_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     notification = (
#         db.query(Notification)
#         .filter(Notification.id == notification_id)
#         .first()
#     )

#     if notification is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Notification not found"
#         )

#     if notification.user_id != current_user.id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You do not have permission to update this notification"
#         )

#     notification.status = "Read"
#     notification.read_at = datetime.utcnow()
#     notification.updated_at = datetime.utcnow()

#     db.commit()
#     db.refresh(notification)

#     return notification


# @router.patch(
#     "/read-all",
#     response_model=list[NotificationResponse]
# )
# def mark_all_notifications_as_read(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     notifications = (
#         db.query(Notification)
#         .filter(
#             Notification.user_id == current_user.id,
#             Notification.status == "Unread"
#         )
#         .all()
#     )

#     now = datetime.utcnow()

#     for notification in notifications:
#         notification.status = "Read"
#         notification.read_at = now
#         notification.updated_at = now

#     db.commit()

#     for notification in notifications:
#         db.refresh(notification)

#     return notifications


# @router.post(
#     "/generate-alerts"
# )
# def generate_alerts(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     renewal_notifications = generate_renewal_reminders(db)
#     obligation_notifications = generate_obligation_alerts(db)

#     return {
#         "renewal_notifications_created": len(
#             renewal_notifications
#         ),
#         "obligation_notifications_created": len(
#             obligation_notifications
#         )
#     }
# def generate_compliance_alerts(
#     db: Session
# ):
#     contracts = (
#         db.query(Contract)
#         .all()
#     )

#     created_notifications = []

#     for contract in contracts:

#         compliance = calculate_contract_compliance(
#             contract.id,
#             db
#         )

#         if compliance["compliance_status"] not in {
#             "Non-Compliant",
#             "High Risk"
#         }:
#             continue

#         user_id = contract.assigned_to or contract.owner_id

#         existing_notification = (
#             db.query(Notification)
#             .filter(
#                 Notification.contract_id == contract.id,
#                 Notification.user_id == user_id,
#                 Notification.notification_type == "Compliance Alert",
#                 Notification.created_at >= datetime.combine(
#                     date.today(),
#                     datetime.min.time()
#                 )
#             )
#             .first()
#         )

#         if existing_notification:
#             continue

#         notification = create_notification(
#             db=db,
#             user_id=user_id,
#             contract_id=contract.id,
#             title="High-Risk Contract Detected",
#             message=(
#                 f"Contract {contract.contract_code} has "
#                 f"{compliance['overdue_obligations']} overdue "
#                 f"obligation(s) and requires attention."
#             ),
#             notification_type="Compliance Alert"
#         )

#         created_notifications.append(notification)

#     return created_notifications


from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
)
from app.core.dependencies import get_current_user
from app.services.notification_service import (
    create_notification,
    generate_renewal_reminders,
    generate_obligation_alerts,
    generate_compliance_alerts,
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# ============================================================
# GET ALL NOTIFICATIONS FOR CURRENT USER
# ============================================================

@router.get(
    "/",
    response_model=list[NotificationResponse]
)
def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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
# GET NOTIFICATION BY ID
# ============================================================

@router.get(
    "/{notification_id}",
    response_model=NotificationResponse
)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id
        )
        .first()
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to access this notification"
            )
        )

    return notification


# ============================================================
# CREATE NOTIFICATION
# ============================================================

@router.post(
    "/",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if notification_data.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You cannot create notifications "
                "for another user"
            )
        )

    try:
        notification = create_notification(
            db=db,
            user_id=notification_data.user_id,
            contract_id=notification_data.contract_id,
            obligation_id=notification_data.obligation_id,
            renewal_id=notification_data.renewal_id,
            notification_type=notification_data.notification_type,
            title=notification_data.title,
            message=notification_data.message,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )

    return notification


# ============================================================
# MARK ONE NOTIFICATION AS READ
# ============================================================

@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse
)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id
        )
        .first()
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to update this notification"
            )
        )

    notification.status = "Read"
    notification.read_at = datetime.utcnow()
    notification.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(notification)

    return notification


# ============================================================
# MARK ALL NOTIFICATIONS AS READ
# ============================================================

@router.patch(
    "/read-all",
    response_model=list[NotificationResponse]
)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id == current_user.id,
            Notification.status == "Unread"
        )
        .all()
    )

    now = datetime.utcnow()

    for notification in notifications:
        notification.status = "Read"
        notification.read_at = now
        notification.updated_at = now

    db.commit()

    for notification in notifications:
        db.refresh(notification)

    return notifications


# ============================================================
# GENERATE AUTOMATIC ALERTS
# ============================================================

@router.post(
    "/generate-alerts"
)
def generate_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    renewal_notifications = (
        generate_renewal_reminders(db)
    )

    obligation_notifications = (
        generate_obligation_alerts(db)
    )

    compliance_notifications = (
        generate_compliance_alerts(db)
    )

    return {
        "renewal_notifications_created": len(
            renewal_notifications
        ),
        "obligation_notifications_created": len(
            obligation_notifications
        ),
        "compliance_notifications_created": len(
            compliance_notifications
        )
    }