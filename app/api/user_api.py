from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.role_checker import RoleChecker, normalize_role, ROLE_ADMIN
from app.database.database import get_db
from app.models.activity import Activity
from app.models.audit_log import AuditLog
from app.models.contract import Contract
from app.models.notification import Notification
from app.models.obligation import Obligation
from app.models.report import Report
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate
from app.services.activity_service import log_activity
from app.utils.security import hash_password

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False
)
def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: User = Depends(RoleChecker([ROLE_ADMIN])),
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.email.ilike(user_data.email.strip())).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    hashed_password = hash_password(user_data.password)

    user = User(
        full_name=user_data.full_name,
        email=user_data.email.strip().lower(),
        password=hashed_password,
        role=user_data.role,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    log_activity(
        db=db,
        action="CREATE_USER",
        entity_type="User",
        entity_id=user.id,
        contract_id=None,
        description=f"Created user {user.full_name} ({user.email}) with role '{user.role}'",
        user=current_user,
        request=request,
    )

    return user


@router.get(
    "",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK
)
@router.get(
    "/",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    include_in_schema=False
)
def get_users(
    current_user: User = Depends(RoleChecker([ROLE_ADMIN])),
    db: Session = Depends(get_db)
):
    users = db.query(User).order_by(User.id.desc()).all()
    return users


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    is_admin = normalize_role(current_user.role) == ROLE_ADMIN
    if not is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this user's profile."
        )

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
    user_data: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    is_admin = normalize_role(current_user.role) == ROLE_ADMIN
    if not is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit another user's profile."
        )

    update_data = user_data.model_dump(exclude_unset=True, exclude_none=True)

    # Non-admins cannot alter roles or active status
    if not is_admin:
        update_data.pop("role", None)
        update_data.pop("is_active", None)

    role_changed = False
    old_role = user.role
    new_role = None

    if "role" in update_data and update_data["role"] != old_role:
        role_changed = True
        new_role = update_data["role"]

    if "password" in update_data:
        user.password = hash_password(update_data.pop("password"))

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    if role_changed:
        log_activity(
            db=db,
            action="ROLE_CHANGE",
            entity_type="User",
            entity_id=user.id,
            contract_id=None,
            description=f"Changed role of user {user.full_name} ({user.email}) from '{old_role}' to '{new_role}'",
            user=current_user,
            request=request,
        )
    else:
        log_activity(
            db=db,
            action="UPDATE_PROFILE",
            entity_type="User",
            entity_id=user.id,
            contract_id=None,
            description=f"Updated user profile for {user.full_name} ({user.email})",
            user=current_user,
            request=request,
        )

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
)
def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker([ROLE_ADMIN])),
):
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own admin account."
        )
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_name = user.full_name
    user_email = user.email

    # Null out dependent foreign keys so DB won't block the delete
    db.query(Activity).filter(Activity.user_id == user_id).update({Activity.user_id: None}, synchronize_session=False)
    db.query(AuditLog).filter(AuditLog.user_id == user_id).update({AuditLog.user_id: None}, synchronize_session=False)
    db.query(Contract).filter(Contract.created_by == user_id).update({Contract.created_by: None}, synchronize_session=False)
    db.query(Notification).filter(Notification.user_id == user_id).update({Notification.user_id: None}, synchronize_session=False)
    db.query(Obligation).filter(Obligation.assigned_to == user_id).update({Obligation.assigned_to: None}, synchronize_session=False)
    db.query(Report).filter(Report.generated_by == user_id).update({Report.generated_by: None}, synchronize_session=False)

    db.delete(user)
    db.commit()

    log_activity(
        db=db,
        action="DELETE_USER",
        entity_type="User",
        entity_id=user_id,
        contract_id=None,
        description=f"Deleted user {user_name} ({user_email})",
        user=current_user,
        request=request,
    )

    return {"message": "User deleted successfully"}