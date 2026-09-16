from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.obligation import Obligation
from app.services.audit_service import create_audit_log


# Administrator user is used as the system audit actor
SYSTEM_AUDIT_USER_ID = 1


def mark_overdue_obligations(db: Session) -> int:
    """
    Mark pending or in-progress obligations as overdue
    when their due date has passed.

    Every automatic status change is recorded in the audit log.
    """

    today = date.today()

    obligations = (
        db.query(Obligation)
        .filter(
            Obligation.due_date.is_not(None),
            Obligation.due_date < today,
            func.lower(Obligation.status).in_(
                ["pending", "in_progress"]
            ),
        )
        .all()
    )

    updated_count = 0

    for obligation in obligations:
        old_status = obligation.status

        obligation.status = "overdue"

        create_audit_log(
            db=db,
            user_id=SYSTEM_AUDIT_USER_ID,
            contract_id=obligation.contract_id,
            action="Automatically marked overdue",
            entity_type="Obligation",
            entity_id=obligation.id,
            details=(
                f"Automatically changed obligation "
                f"'{obligation.title}' status from "
                f"'{old_status}' to 'overdue' because "
                f"the due date ({obligation.due_date}) has passed"
            ),
        )

        updated_count += 1

    if updated_count:
        db.commit()

    return updated_count