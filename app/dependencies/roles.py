from fastapi import Depends, HTTPException, status
from app.dependencies.auth import get_current_user
from app.schemas.permissions import ROLE_PERMISSIONS


class PermissionChecker:
    def __init__(self, permission: str):
        self.permission = permission

    def __call__(self, current_user=Depends(get_current_user)):
        permissions = ROLE_PERMISSIONS.get(current_user.role, [])

        if self.permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )

        return current_user