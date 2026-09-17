from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogResponse
from app.utils.authorization import get_current_user


router = APIRouter(
    prefix="/audit-history",
    tags=["Audit History"]
)


@router.get(
    "",
    response_model=list[AuditLogResponse]
)
def get_audit_history(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(AuditLog).order_by(
        AuditLog.created_at.desc()
    ).all()
