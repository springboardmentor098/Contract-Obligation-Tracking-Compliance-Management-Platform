from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models.contract_compliance import ContractCompliance


def calculate_compliance(obligations):
    """
    Calculate compliance information for a contract
    based on its obligations.
    """

    total = len(obligations)

    completed = 0
    pending = 0
    delayed = 0
    overdue = 0

    today = date.today()

    for obligation in obligations:

        # Completed obligation
        if obligation.status == "Completed":
            completed += 1
            continue

        # Overdue obligation
        if obligation.due_date and obligation.due_date < today:
            overdue += 1
            continue

        # Delayed obligation
        if obligation.status == "Delayed":
            delayed += 1
            continue

        # Pending / In Progress
        if obligation.status in ["Pending", "In Progress"]:
            pending += 1
            continue

        # Unknown non-completed status
        pending += 1

    # Compliance score
    if total == 0:
        compliance_score = 100.0
    else:
        compliance_score = round(
            (completed / total) * 100,
            2
        )

    # Compliance status
    if overdue >= 2:
        compliance_status = "High Risk"

    elif overdue >= 1:
        compliance_status = "Non-Compliant"

    elif delayed >= 1:
        compliance_status = "Delayed"

    elif pending >= 1:
        compliance_status = "Pending"

    else:
        compliance_status = "Compliant"

    # Risk level
    if overdue >= 2:
        risk_level = "High"

    elif overdue == 1:
        risk_level = "Medium"

    else:
        risk_level = "Low"

    return {
        "compliance_status": compliance_status,
        "compliance_score": compliance_score,
        "total_obligations": total,
        "completed_obligations": completed,
        "pending_obligations": pending,
        "delayed_obligations": delayed,
        "overdue_obligations": overdue,
        "risk_level": risk_level,
    }


def save_compliance_record(
    db: Session,
    contract_id: int,
    compliance_result: dict,
    notes: str | None = None
):
    """
    Save a compliance evaluation result
    into the contract_compliance table.
    """

    record = ContractCompliance(
        contract_id=contract_id,
        status=compliance_result["compliance_status"],
        compliance_score=compliance_result["compliance_score"],
        risk_level=compliance_result["risk_level"],
        notes=notes,
        evaluated_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record