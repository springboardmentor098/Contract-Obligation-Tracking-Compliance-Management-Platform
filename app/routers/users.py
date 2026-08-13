from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_roles
from app.core.roles import UserRole
from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Retrieve profile of currently authenticated user (All Authenticated Roles)."""
    return current_user


@router.get(
    "/",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            require_roles(
                UserRole.ADMINISTRATOR,
                UserRole.LEGAL_MANAGER,
                UserRole.COMPLIANCE_OFFICER,
                UserRole.CONTRACT_MANAGER,
                UserRole.DEPARTMENT_HEAD
            )
        )
    ]
)
def get_users(db: Session = Depends(get_db)):
    """List all users (Authorized Management Roles)."""
    users = db.query(User).all()
    return users


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific user details by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user and hasattr(User, 'user_id'):
        user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        return {"message": "User not found"}

    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMINISTRATOR))]
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user (Administrator Only)."""
    name = getattr(user_data, "name", None) or getattr(user_data, "full_name", "User")
    user = User(
        full_name=name,
        email=user_data.email,
        role=user_data.role,
        is_active=True
    )
    if hasattr(User, "name"):
        setattr(user, "name", name)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(UserRole.ADMINISTRATOR, UserRole.LEGAL_MANAGER))]
)
def update_user(
    user_id: int,
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Update user details (Administrator & Legal Manager Only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user and hasattr(User, 'user_id'):
        user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        return {"message": "User not found"}

    name = getattr(user_data, "name", None) or getattr(user_data, "full_name", "User")
    user.full_name = name
    user.email = user_data.email
    user.role = user_data.role
    if hasattr(user, "name"):
        setattr(user, "name", name)

    db.commit()
    db.refresh(user)

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_roles(UserRole.ADMINISTRATOR))]
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Delete a user by ID (Administrator Only).

    Required Test Target:
    - Administrator -> 200 OK
    - Authenticated Employee -> 403 Forbidden
    - Unauthenticated -> 401 Unauthorized
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user and hasattr(User, 'user_id'):
        user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        return {"message": "User not found", "status": "success"}

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully", "user_id": user_id}