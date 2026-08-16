from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.roles import PermissionChecker
from app.models.user import User
from app.database.database import get_db
from app.schemas.user import UserCreate, UserResponse
from app.services.user import (
    register_user,
    get_all_users,
    get_user_by_id,
    update_user_service,
    delete_user_service,
)

router = APIRouter()


# CREATE USER
@router.post(
    "/db/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user_db(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("create_user"))
):
    try:
        return register_user(db, user_data)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# GET ALL USERS
@router.get(
    "/db/users",
    response_model=list[UserResponse]
)
def get_users_db(
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("view_user"))
):
    return get_all_users(db)


# GET USER BY ID
@router.get(
    "/users/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("view_user"))
):
    user = get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# UPDATE USER
@router.put(
    "/users/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: int,
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("update_user"))
):
    try:
        return update_user_service(db, user_id, user_data)

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


# DELETE USER
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(PermissionChecker("delete_user"))
):
    try:
        return delete_user_service(db, user_id)

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )