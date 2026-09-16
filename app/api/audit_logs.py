from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.audit_log import AuditLog
from app.core.dependencies import require_permission
from app.core.permissions import Permission


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


# =========================================================
# LIST AUDIT LOGS
# =========================================================

@router.get("")
def list_audit_logs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.READ_AUDIT_LOG)
    ),
):
    return (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .all()
    )
