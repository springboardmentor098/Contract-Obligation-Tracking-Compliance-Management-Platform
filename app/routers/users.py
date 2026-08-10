from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.core.security import hash_password

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# Create User
@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        role=user_data.role,
        password=hash_password(user_data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# Get All Users
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


# Get User by ID
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
        return {"error": f"User {user_id} not found"}

    return user


# Update User
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
        return {"error": f"User {user_id} not found"}

    user.full_name = user_data.full_name
    user.email = user_data.email
    user.role = user_data.role
    user.password = hash_password(user_data.password)

    db.commit()
    db.refresh(user)

    return user


# Delete User
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {"error": f"User {user_id} not found"}

    db.delete(user)
    db.commit()

    return {"message": f"User {user_id} deleted successfully"}