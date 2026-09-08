from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.rbac import UserRole
from app.database.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit import AuditLogListResponse, AuditLogResponse


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit History"],
)


def check_audit_access(current_user: User) -> None:
    """
    Only Administrators and Compliance Officers can access audit history.
    """
    allowed_roles = {
        UserRole.ADMINISTRATOR.value,
        UserRole.COMPLIANCE_OFFICER.value,
    }

    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrator or Compliance Officer can access audit history",
        )


@router.get(
    "",
    response_model=AuditLogListResponse,
)
def get_audit_logs(
    entity_type: str | None = Query(default=None),
    action: str | None = Query(default=None),
    user_id: UUID | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return audit history for authorized users.

    Administrators and Compliance Officers can view audit logs.
    Supports filtering by entity type, action, user and date range.
    """

    check_audit_access(current_user)

    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_from must be earlier than or equal to date_to",
        )

    query = select(AuditLog)
    count_query = select(func.count()).select_from(AuditLog)

    if entity_type:
        condition = AuditLog.entity_type.ilike(f"%{entity_type}%")
        query = query.where(condition)
        count_query = count_query.where(condition)

    if action:
        condition = AuditLog.action.ilike(f"%{action}%")
        query = query.where(condition)
        count_query = count_query.where(condition)

    if user_id:
        condition = AuditLog.user_id == user_id
        query = query.where(condition)
        count_query = count_query.where(condition)

    if date_from:
        condition = AuditLog.created_at >= date_from
        query = query.where(condition)
        count_query = count_query.where(condition)

    if date_to:
        condition = AuditLog.created_at <= date_to
        query = query.where(condition)
        count_query = count_query.where(condition)

    query = (
        query
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    audit_logs = db.scalars(query).all()
    total = db.scalar(count_query) or 0

    return AuditLogListResponse(
        data=audit_logs,
        total=total,
    )


@router.get(
    "/{audit_log_id}",
    response_model=AuditLogResponse,
)
def get_audit_log(
    audit_log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return one audit log entry.
    """

    check_audit_access(current_user)

    audit_log = db.scalar(
        select(AuditLog).where(AuditLog.id == audit_log_id)
    )

    if audit_log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found",
        )

    return audit_log