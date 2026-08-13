from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.roles import UserRole
from app.core.security import decode_access_token
from app.database.database import get_db
from app.models.user import User

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("user_id") or payload.get("sub")
    email = payload.get("email")

    user = None
    if user_id:
        try:
            uid = int(user_id)
            user = db.query(User).filter(User.user_id == uid).first()
        except Exception:
            user = None
    if not user and email:
        user = db.query(User).filter(User.email == email).first()

    if not user:
        # If user not found in DB but payload contains valid JWT data, construct transient User object
        role = payload.get("role", UserRole.EMPLOYEE.value)
        name = payload.get("name") or payload.get("full_name") or "User"
        user = User(
            user_id=int(user_id) if user_id and str(user_id).isdigit() else 1,
            name=name,
            email=email or "user@contractiq.com",
            password_hash="hash",
            role=role,
            is_active=True
        )

    if hasattr(user, "is_active") and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


class RoleChecker:
    """Reusable dependency to enforce role-based permissions."""
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = [r.value if isinstance(r, UserRole) else str(r) for r in allowed_roles]

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        user_role = getattr(current_user, "role", None)
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: You do not have sufficient permissions to perform this action. Required role: {', '.join(self.allowed_roles)}"
            )
        return current_user


def require_roles(*roles: UserRole):
    """Convenience dependency generator for role checking."""
    return RoleChecker(list(roles))
