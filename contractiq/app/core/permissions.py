"""
Reusable role-based authorization mechanism (Sprint 6).

Usage:
    @router.delete("/users/{user_id}")
    def delete_user(
        user_id: int,
        current_user: User = Depends(require_roles(UserRole.ADMINISTRATOR)),
    ):
        ...

`require_roles` returns a FastAPI dependency. Because it itself depends on
`get_current_active_user`, a request with a missing/invalid JWT will already
have failed with 401 before the role check ever runs. If the JWT is valid
but the user's role is not in the allowed set, a 403 is raised.
"""

from typing import Callable, Iterable

from fastapi import Depends, HTTPException, status

from app.core.deps import get_current_active_user
from app.models.user import User, UserRole


def require_roles(*allowed_roles: UserRole) -> Callable[..., User]:
    allowed: Iterable[UserRole] = allowed_roles

    def dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return dependency


# Convenience role groups used across routers
ANY_MANAGER_ROLES = (
    UserRole.ADMINISTRATOR,
    UserRole.LEGAL_MANAGER,
    UserRole.CONTRACT_MANAGER,
)

COMPLIANCE_VIEW_ROLES = (
    UserRole.ADMINISTRATOR,
    UserRole.LEGAL_MANAGER,
    UserRole.COMPLIANCE_OFFICER,
    UserRole.CONTRACT_MANAGER,
)

APPROVAL_ROLES = (UserRole.ADMINISTRATOR, UserRole.LEGAL_MANAGER)
