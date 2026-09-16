from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserUpdate, PasswordChange, UserResponse
from app.core.security import hash_password
from app.core.dependencies import require_permission
from app.core.permissions import Permission


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# =========================================================
# CREATE USER
# Administrator only
# =========================================================

@router.post(
    "/",
    response_model=UserResponse,
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.MANAGE_USERS)
    ),
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        is_active=True,
        hashed_password=hash_password(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# =========================================================
# GET ALL USERS
# Administrator / users with READ_USERS
# =========================================================

@router.get(
    "/",
    response_model=list[UserResponse],
)
def get_users(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.READ_USERS)
    ),
):
    return db.query(User).all()


# =========================================================
# GET USER BY ID
# =========================================================

@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.READ_USERS)
    ),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


# =========================================================
# UPDATE USER
# =========================================================

@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    updated_user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.UPDATE_USERS)
    ),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # Prevent email collision
    existing_user = (
        db.query(User)
        .filter(
            User.email == updated_user.email,
            User.id != user_id,
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    user.full_name = updated_user.full_name
    user.email = updated_user.email
    user.role = updated_user.role
    user.is_active = updated_user.is_active


    db.commit()
    db.refresh(user)

    return user

# =========================================================
# DEACTIVATE USER
# Administrator / users with DELETE_USERS permission
# =========================================================

@router.delete(
    "/{user_id}",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.DELETE_USERS)
    ),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # Prevent deactivating the last active Administrator
    if user.role == "Administrator" and user.is_active:
        active_admin_count = (
            db.query(User)
            .filter(
                User.role == "Administrator",
                User.is_active.is_(True),
            )
            .count()
        )

        if active_admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot deactivate the last active Administrator",
            )

    user.is_active = False

    db.commit()
    db.refresh(user)

    return {
        "message": "User deactivated successfully",
        "user_id": user.id,
        "is_active": user.is_active,
    }

# =========================================================
# CHANGE USER PASSWORD
# Users with UPDATE_USERS permission
# =========================================================

@router.patch(
    "/{user_id}/password",
)
def change_user_password(
    user_id: int,
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.UPDATE_USERS)
    ),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user.hashed_password = hash_password(
        password_data.password
    )

    db.commit()

    return {
        "message": "Password changed successfully"
    }
