from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    user_id: int,
    action: str,
    entity_type: str | None = None,
    entity_id: int | None = None,
    old_values=None,
    new_values=None,
    ip_address: str | None = None,
):
    audit_log = AuditLog(
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address,
        created_at=datetime.now(timezone.utc),
    )

    db.add(audit_log)

    return audit_log
