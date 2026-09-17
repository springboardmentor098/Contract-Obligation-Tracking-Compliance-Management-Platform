from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.activity import Activity
from app.models.audit_log import AuditLog
from app.models.user import User
from app.core.dependencies import require_role

router = APIRouter(
    prefix="/audit",
    tags=["Audit / Activity"]
)


@router.get("/activities")
def get_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Administrator"))
):
    activities = (
        db.query(Activity)
        .order_by(Activity.created_at.desc())
        .all()
    )

    return [
        {
            "id": activity.id,
            "user_id": activity.user_id,
            "contract_id": activity.contract_id,
            "activity_type": activity.activity_type,
            "description": activity.description,
            "created_at": activity.created_at,
        }
        for activity in activities
    ]


@router.get("/logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Administrator"))
):
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "contract_id": log.contract_id,
            "action": log.action,
            "details": log.details,
            "created_at": log.created_at,
        }
        for log in logs
    ]
