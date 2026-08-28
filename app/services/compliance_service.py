from datetime import date

from sqlalchemy.orm import Session

from app.models.obligation import Obligation
from app.models.compliance import ComplianceRecord


def calculate_contract_compliance(obligations):
    total_obligations = len(obligations)

    completed_obligations = 0
    pending_obligations = 0
    overdue_obligations = 0
    delayed_obligations = 0

    for obligation in obligations:
        if obligation.status == "Completed":
            completed_obligations += 1

        elif obligation.due_date < date.today():
            overdue_obligations += 1

        elif obligation.status == "In Progress":
            delayed_obligations += 1

        else:
            pending_obligations += 1

    if total_obligations == 0:
        compliance_score = 100
    else:
        compliance_score = round(
            (completed_obligations / total_obligations) * 100,
            2
        )

    if overdue_obligations >= 2:
        compliance_status = "High Risk"
        risk_level = "High"

    elif overdue_obligations == 1:
        compliance_status = "Non-Compliant"
        risk_level = "Medium"

    elif delayed_obligations > 0:
        compliance_status = "Delayed"
        risk_level = "Low"

    elif pending_obligations > 0:
        compliance_status = "Pending"
        risk_level = "Low"

    else:
        compliance_status = "Compliant"
        risk_level = "Low"

    return {
        "total_obligations": total_obligations,
        "completed_obligations": completed_obligations,
        "pending_obligations": pending_obligations,
        "overdue_obligations": overdue_obligations,
        "delayed_obligations": delayed_obligations,
        "compliance_score": compliance_score,
        "compliance_status": compliance_status,
        "risk_level": risk_level
    }
def save_compliance_history(
    db: Session,
    contract_id: int,
    compliance_data: dict
):
    record = ComplianceRecord(
        contract_id=contract_id,
        status=compliance_data["compliance_status"],
        compliance_score=compliance_data["compliance_score"],
        risk_level=compliance_data["risk_level"],
        notes="Automatically generated compliance evaluation"
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record