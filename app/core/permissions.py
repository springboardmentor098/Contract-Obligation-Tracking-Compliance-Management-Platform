from typing import List
from fastapi import HTTPException, Depends, status
from app.core.roles import UserRole
from app.core.security import get_current_user, normalize_role_name


class RoleChecker:
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = {
            normalize_role_name(role.value if hasattr(role, "value") else str(role))
            for role in allowed_roles
            if normalize_role_name(role.value if hasattr(role, "value") else str(role))
        }

    def __call__(self, current_user: dict = Depends(get_current_user)):
        user_role = normalize_role_name(current_user.get("role"))

        if not user_role or user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have enough permissions to perform this action"
            )
        return current_user