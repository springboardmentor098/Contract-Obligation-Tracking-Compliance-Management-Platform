
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.all_models import User
from app.schemas.user_schema import UserCreate, UserResponse
from app.core.security import get_password_hash
from app.core.permissions import RoleChecker
from app.core.roles import UserRole

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)
require_admin = RoleChecker([UserRole.ADMINISTRATOR])
require_auth = RoleChecker([UserRole.ADMINISTRATOR, UserRole.EMPLOYEE])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)): 
    
    # 1. Hash the password
    hashed_pw = get_password_hash(user.password)

    # 2. Save it to PostgreSQL
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        hashed_password=hashed_pw 
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
@router.get(
    "/",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK
)
# Add the current_user dependency here:
def get_users(db: Session = Depends(get_db), current_user: dict = Depends(require_auth)):
    users = db.query(User).all()
    return users

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return None

# GET a specific user by their ID
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_auth)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# PUT (Update) a specific user by their ID
@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK
)
def update_user(
    user_id: int, 
    user_data: UserCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)  #  Security lock added here!
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.full_name = user_data.full_name
    user.email = user_data.email
    user.role = user_data.role
    
    db.commit()
    db.refresh(user)
    return user