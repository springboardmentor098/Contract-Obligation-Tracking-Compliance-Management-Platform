from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    user_id: int,
    action: str,
    entity_type: str,
    entity_id: int,
    contract_id: int | None = None,
    details: str | None = None,
):
    audit_log = AuditLog(
        user_id=user_id,
        contract_id=contract_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )

    db.add(audit_log)

    return audit_log