# from fastapi import APIRouter, Depends,status
# from sqlalchemy.orm import Session

# from app.database.database import get_db
# from app.models.user import User
# from app.schemas.user import UserCreate, UserResponse

# router = APIRouter(
#     prefix="/users",
#     tags=["Users"]
# )

# @router.post(
#     "/",
#     response_model=UserResponse,
#     status_code=201
# )
# def create_user(
#     user_data: UserCreate,
#     db: Session = Depends(get_db)
# ):
#     user = User(
#         full_name=user_data.full_name,
#         email=user_data.email,
#         role=user_data.role
#     )

#     db.add(user)
#     db.commit()
#     db.refresh(user)

#     return user

# @router.get(
#     "/",
#     response_model=list[UserResponse],
#     status_code=status.HTTP_200_OK
# )
# def get_users(db: Session = Depends(get_db)):
#     users = db.query(User).all()
#     return users


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# Create User
@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        role=user_data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# Get All Users
@router.get(
    "/",
    response_model=list[UserResponse]
)
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


# Get User By ID
@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# Update User
@router.put(
    "/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.full_name = user_data.full_name
    user.email = user_data.email
    user.role = user_data.role
    user.is_active = user_data.is_active

    db.commit()
    db.refresh(user)

    return user


# Delete User
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }