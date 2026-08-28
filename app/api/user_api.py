from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.models.activity import Activity
from app.models.audit_log import AuditLog
from app.models.contract_version import ContractVersion
from app.models.contract import Contract
from app.models.notification import Notification
from app.models.obligation import Obligation
from app.models.report import Report
from app.schemas.user_schema import UserCreate, UserResponse
from app.utils.security import hash_password
from fastapi import Depends
from app.core.role_checker import RoleChecker

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    hashed_password = hash_password(user_data.password)

    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password=hashed_password,
        role=user_data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.get(
    "/",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK
)
def get_users(
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return users


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)
def update_user(
    user_id: int,
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    hashed_password = hash_password(user_data.password)

    user.full_name = user_data.full_name
    user.email = user_data.email
    user.password = hashed_password
    user.role = user_data.role

    db.commit()
    db.refresh(user)

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["Administrator"])),
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Null out dependent foreign keys so DB won't block the delete
    db.query(Activity).filter(Activity.user_id == user_id).update({Activity.user_id: None}, synchronize_session=False)
    db.query(AuditLog).filter(AuditLog.user_id == user_id).update({AuditLog.user_id: None}, synchronize_session=False)
    db.query(ContractVersion).filter(ContractVersion.uploaded_by == user_id).update({ContractVersion.uploaded_by: None}, synchronize_session=False)
    db.query(Contract).filter(Contract.created_by == user_id).update({Contract.created_by: None}, synchronize_session=False)
    db.query(Notification).filter(Notification.user_id == user_id).update({Notification.user_id: None}, synchronize_session=False)
    db.query(Obligation).filter(Obligation.assigned_to == user_id).update({Obligation.assigned_to: None}, synchronize_session=False)
    db.query(Report).filter(Report.generated_by == user_id).update({Report.generated_by: None}, synchronize_session=False)

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}