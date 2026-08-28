from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.audit_log import AuditLog
from app.schemas.audit_log_schema import AuditLogCreate, AuditLogResponse


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"]
)


@router.post(
    "",
    response_model=AuditLogResponse,
    status_code=status.HTTP_201_CREATED
)
def create_audit_log(
    audit_data: AuditLogCreate,
    db: Session = Depends(get_db)
):
    audit_log = AuditLog(
        user_id=audit_data.user_id,
        action=audit_data.action,
        table_name=audit_data.table_name,
        record_id=audit_data.record_id
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log


@router.get(
    "/",
    response_model=list[AuditLogResponse]
)
def get_audit_logs(
    db: Session = Depends(get_db)
):
    return db.query(AuditLog).all()


@router.get(
    "/{audit_log_id}",
    response_model=AuditLogResponse
)
def get_audit_log(
    audit_log_id: int,
    db: Session = Depends(get_db)
):
    audit_log = db.query(AuditLog).filter(
        AuditLog.id == audit_log_id
    ).first()

    if not audit_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )

    return audit_log