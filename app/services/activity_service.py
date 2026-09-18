from datetime import datetime, timezone
from typing import Any
from fastapi import Request
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.user import User


def get_client_ip(request: Request | None) -> str | None:
    """Extracts client IP address safely from request headers or host."""
    if not request:
        return None

    # Check X-Forwarded-For if behind a proxy / load balancer
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # Take the first IP if multiple are listed
        return forwarded.split(",")[0].strip()

    # Check X-Real-IP
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    if getattr(request, "client", None) and getattr(request.client, "host", None):
        return request.client.host

    return None


def log_activity(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    description: str | None = None,
    user: User | None = None,
    user_id: int | None = None,
    user_name: str | None = None,
    user_role: str | None = None,
    contract_id: int | None = None,
    status: str = "Success",
    request: Request | None = None,
    metadata: dict[str, Any] | None = None,
    commit: bool = True,
) -> Activity:
    """
    Creates and persists an activity log in PostgreSQL with all required metadata:
    - User Name
    - User Role
    - Action
    - Entity Type
    - Entity ID
    - Description
    - Timestamp
    - Status
    - IP Address
    """
    now = datetime.now(timezone.utc)

    # Determine user attributes
    effective_user_id = user.id if user else user_id
    effective_user_name = (
        user.full_name
        if (user and getattr(user, "full_name", None))
        else (user_name or (f"User #{effective_user_id}" if effective_user_id else "System"))
    )
    effective_user_role = (
        user.role
        if (user and getattr(user, "role", None))
        else (user_role or "System")
    )

    # Fallback description if not explicitly provided
    effective_desc = description or f"{action} on {entity_type} {entity_id or ''}".strip()
    client_ip = get_client_ip(request)

    activity = Activity(
        user_id=effective_user_id,
        user_name=effective_user_name,
        user_role=effective_user_role,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=effective_desc,
        activity=effective_desc,
        status=status,
        ip_address=client_ip,
        contract_id=contract_id,
        created_at=now,
        timestamp=now,
        metadata_json=metadata,
    )

    db.add(activity)

    if commit:
        try:
            db.commit()
            db.refresh(activity)
        except Exception:
            db.rollback()
            raise

    return activity
