from typing import List
from fastapi import HTTPException, Depends, status
from app.core.roles import UserRole

#  Fixed import: Pointing to the new security file we just updated
from app.core.security import get_current_user 

class RoleChecker:
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    #  Fixed type: JWTs return a dictionary, not a User model
    def __call__(self, current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        
        if user_role not in [role.value for role in self.allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have enough permissions to perform this action"
            )
        return current_user