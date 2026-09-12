from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.audit_log import AuditLog


router = APIRouter(
    prefix="/audit",
    tags=["Audit & Activity"]
)


@router.get(
    "/logs",
    status_code=status.HTTP_200_OK
)
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Return audit history for authenticated users.
    """

    audit_logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "old_values": log.old_values,
            "new_values": log.new_values,
            "ip_address": log.ip_address,
            "created_at": log.created_at
        }
        for log in audit_logs
    ]