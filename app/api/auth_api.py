from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, get_optional_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.auth_schema import Token
from app.services.activity_service import log_activity
from app.utils.security import verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # OAuth2 calls this field username, but ContractIQ authenticates by email.
    email = form_data.username.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    try:
        password_matches = verify_password(form_data.password, user.password)
    except Exception:
        # A malformed, corrupted, or non-bcrypt database value is safely treated as non-matching
        password_matches = False

    if not password_matches:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    user.last_login = datetime.now(timezone.utc)
    db.commit()

    # Automatically record USER_LOGIN activity log
    log_activity(
        db=db,
        action="USER_LOGIN",
        entity_type="User",
        entity_id=user.id,
        description=f"User {user.email} logged in successfully",
        user=user,
        status="Success",
        request=request,
    )

    access_token = create_access_token(
        data={
            "sub": user.email,
            "role": user.role,
            "user_id": user.id,
            "name": user.full_name,
            "avatar_url": user.avatar_url,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.full_name,
            "role": user.role,
            "avatar_url": user.avatar_url,
        },
    }


@router.post("/logout")
def logout(
    request: Request,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """Logs out the user and records the logout activity."""
    if current_user:
        log_activity(
            db=db,
            action="USER_LOGOUT",
            entity_type="User",
            entity_id=current_user.id,
            description=f"User {current_user.email} logged out",
            user=current_user,
            status="Success",
            request=request,
        )

    return {"message": "Logged out successfully"}
