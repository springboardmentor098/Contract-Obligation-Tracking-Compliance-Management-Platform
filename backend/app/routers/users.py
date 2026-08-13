from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import require_roles
from app.core.rbac import UserRole
from app.database.database import get_db
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserResponse
from app.utils.security import hash_password


router = APIRouter()


# ============================================================
# CREATE USER
# ============================================================

@router.post(
    "/db/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_db(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    user = UserModel(
        full_name=user_data.full_name,
        email=user_data.email,
        role=user_data.role.value,
        password_hash=hash_password(user_data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# ============================================================
# GET ALL USERS
# ============================================================

@router.get(
    "/db/users",
    response_model=list[UserResponse],
)
def get_users_db(
    db: Session = Depends(get_db),
):
    users = db.query(UserModel).all()
    return users


# ============================================================
# GET USER BY ID
# ============================================================

@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    user = (
        db.query(UserModel)
        .filter(UserModel.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


# ============================================================
# UPDATE USER - ADMINISTRATOR ONLY
# ============================================================

@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: UUID,
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(
        require_roles(UserRole.ADMINISTRATOR)
    ),
):
    user = (
        db.query(UserModel)
        .filter(UserModel.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.full_name = user_data.full_name
    user.email = user_data.email
    user.role = user_data.role.value
    user.password_hash = hash_password(user_data.password)

    db.commit()
    db.refresh(user)

    return user


# ============================================================
# DELETE USER - ADMINISTRATOR ONLY
# ============================================================

@router.delete("/users/{user_id}")
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(
        require_roles(UserRole.ADMINISTRATOR)
    ),
):
    user = (
        db.query(UserModel)
        .filter(UserModel.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully",
    }