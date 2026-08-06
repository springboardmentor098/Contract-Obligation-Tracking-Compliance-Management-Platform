from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# -----------------------------
# Create Single User
# -----------------------------
@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
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
            status_code=400,
            detail="Email already exists"
        )

    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        role=user_data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# -----------------------------
# Create Multiple Users
# -----------------------------
@router.post(
    "/bulk",
    response_model=list[UserResponse],
    status_code=status.HTTP_201_CREATED
)
def create_multiple_users(
    users: List[UserCreate],
    db: Session = Depends(get_db)
):
    created_users = []

    for user_data in users:

        existing_user = db.query(User).filter(
            User.email == user_data.email
        ).first()

        if existing_user:
            continue

        user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            role=user_data.role
        )

        db.add(user)
        created_users.append(user)

    db.commit()

    for user in created_users:
        db.refresh(user)

    return created_users


# -----------------------------
# Get All Users
# -----------------------------
@router.get(
    "/",
    response_model=list[UserResponse]
)
def get_users(
    db: Session = Depends(get_db)
):
    return db.query(User).all()


# -----------------------------
# Get User By ID
# -----------------------------
@router.get(
    "/{user_id}",
    response_model=UserResponse
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
            status_code=404,
            detail="User not found"
        )

    return user


# -----------------------------
# Update User
# -----------------------------
@router.put(
    "/{user_id}",
    response_model=UserResponse
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
            status_code=404,
            detail="User not found"
        )

    user.full_name = user_data.full_name
    user.email = user_data.email
    user.role = user_data.role

    db.commit()
    db.refresh(user)

    return user


# -----------------------------
# Delete User
# -----------------------------
@router.delete(
    "/{user_id}"
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
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }