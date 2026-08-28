from fastapi import Depends, HTTPException, status

from app.core.auth import get_current_user
from app.models.user import User


class RoleChecker:
    def __init__(self, allowed_roles):
        self.allowed_roles = set(allowed_roles)

    def __call__(self, current_user: User = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to perform this action.",
            )

        return current_user