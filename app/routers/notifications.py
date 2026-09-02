from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database.database import get_db
from app.models.all_models import Notification, NotificationStatusEnum
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.core.security import get_current_user
from app.services.notification_service import create_notification

router = APIRouter(tags=["Notifications"])

# Helper to safely extract user ID from the JWT token payload
def get_user_id(current_user: dict):
    return current_user.get("id") or current_user.get("sub")

# 1. Get All Notifications for Current User
@router.get("/notifications", response_model=List[NotificationResponse], status_code=status.HTTP_200_OK)
def get_my_notifications(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = get_user_id(current_user)
    return db.query(Notification).filter(Notification.user_id == user_id).all()

# 2. Get Notification by ID (Protected against unauthorized access)
@router.get("/notifications/{notification_id}", response_model=NotificationResponse, status_code=status.HTTP_200_OK)
def get_notification(notification_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = get_user_id(current_user)
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification Not Found")
    if str(notif.user_id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accessing Another User's Notification is Forbidden")
        
    return notif

# 3. Create Notification
@router.post("/notifications", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_new_notification(notif_data: NotificationCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return create_notification(
        db=db,
        user_id=notif_data.user_id,
        title=notif_data.title,
        message=notif_data.message,
        notif_type=notif_data.notification_type,
        contract_id=notif_data.contract_id,
        obligation_id=notif_data.obligation_id
    )

# 4. Mark Notification as Read
@router.patch("/notifications/{notification_id}/read", response_model=NotificationResponse, status_code=status.HTTP_200_OK)
def mark_notification_read(notification_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = get_user_id(current_user)
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification Not Found")
    if str(notif.user_id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        
    notif.status = NotificationStatusEnum.READ
    notif.read_at = datetime.utcnow()
    db.commit()
    db.refresh(notif)
    return notif

# 5. Mark All as Read
@router.patch("/notifications/read-all", status_code=status.HTTP_200_OK)
def mark_all_read(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = get_user_id(current_user)
    unread_notifs = db.query(Notification).filter(
        Notification.user_id == user_id, 
        Notification.status == NotificationStatusEnum.UNREAD
    ).all()
    
    for notif in unread_notifs:
        notif.status = NotificationStatusEnum.READ
        notif.read_at = datetime.utcnow()
        
    db.commit()
    return {"message": f"{len(unread_notifs)} notifications marked as read"}