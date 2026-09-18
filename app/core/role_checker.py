from typing import Iterable, Set
from fastapi import Depends, HTTPException, status

from app.core.auth import get_current_user
from app.models.user import User

# Standard Role Constants
ROLE_ADMIN = "Admin"
ROLE_LEGAL_MANAGER = "Legal Manager"
ROLE_CONTRACT_MANAGER = "Contract Manager"
ROLE_COMPLIANCE_OFFICER = "Compliance Officer"
ROLE_VIEWER = "Viewer"

ALL_ROLES = [
    ROLE_ADMIN,
    ROLE_LEGAL_MANAGER,
    ROLE_CONTRACT_MANAGER,
    ROLE_COMPLIANCE_OFFICER,
    ROLE_VIEWER,
]


def normalize_role(role: str | None) -> str:
    """Normalizes role string with case-insensitivity and admin alias handling."""
    if not role:
        return ""
    cleaned = str(role).strip()
    lower = cleaned.lower()
    if lower in ("admin", "administrator"):
        return ROLE_ADMIN
    if lower == "legal manager":
        return ROLE_LEGAL_MANAGER
    if lower == "contract manager":
        return ROLE_CONTRACT_MANAGER
    if lower == "compliance officer":
        return ROLE_COMPLIANCE_OFFICER
    if lower == "viewer":
        return ROLE_VIEWER
    return cleaned


class RoleChecker:
    """
    FastAPI dependency for verifying that the authenticated user possesses
    one of the allowed roles. Returns HTTP 403 Forbidden on authorization failure.
    """

    def __init__(self, allowed_roles: Iterable[str]):
        self.allowed_roles: Set[str] = {normalize_role(r) for r in allowed_roles}
        # If Admin is included, allow Administrator alias as well
        if ROLE_ADMIN in self.allowed_roles:
            self.allowed_roles.add("Administrator")

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        user_role_normalized = normalize_role(current_user.role)

        if user_role_normalized not in self.allowed_roles and current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )

        return current_user


# Common reusable dependency instances
require_admin = RoleChecker([ROLE_ADMIN])
require_non_viewer = RoleChecker([
    ROLE_ADMIN,
    ROLE_LEGAL_MANAGER,
    ROLE_CONTRACT_MANAGER,
    ROLE_COMPLIANCE_OFFICER,
])