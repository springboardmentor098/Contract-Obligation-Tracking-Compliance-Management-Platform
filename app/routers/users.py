
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse  # type: ignore[reportMissingImports]

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post(
    "",
    response_model=UserResponse,
    status_code=201
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
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
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users