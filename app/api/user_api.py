from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse
from app.middleware.auth import require_roles
from app.core.security import hash_password


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ============================================================
# CREATE USER
# Only Administrator can create users
# ============================================================

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_roles("Administrator"))
    ]
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        role=user_data.role,
        password_hash=hash_password(user_data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# ============================================================
# GET ALL USERS
# Only Administrator can view all users
# ============================================================

@router.get(
    "",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_roles("Administrator"))
    ]
)
def get_users(
    db: Session = Depends(get_db)
):
    users = db.query(User).all()

    return users


# ============================================================
# GET USER BY ID
# Only Administrator can view a user's details
# ============================================================

@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_roles("Administrator"))
    ]
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# ============================================================
# UPDATE USER
# Only Administrator can update users
# ============================================================

@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_roles("Administrator"))
    ]
)
def update_user(
    user_id: int,
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    existing_user = db.query(User).filter(
        User.email == user_data.email,
        User.id != user_id
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    user.full_name = user_data.full_name
    user.email = user_data.email
    user.role = user_data.role
    user.password_hash = hash_password(user_data.password)

    db.commit()
    db.refresh(user)

    return user


# ============================================================
# DELETE USER
# Only Administrator can delete users
# ============================================================

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_roles("Administrator"))
    ]
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }