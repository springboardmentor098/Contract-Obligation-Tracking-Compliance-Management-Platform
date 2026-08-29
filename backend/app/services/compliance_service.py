from sqlalchemy.orm import Session

from backend.app.models.contract import Contract
from backend.app.models.obligation import Obligation


def calculate_contract_compliance(
    contract: Contract,
    db: Session
):
    # Get all obligations for this contract
    obligations = db.query(Obligation).filter(
        Obligation.contract_id == contract.id
    ).all()

    total_obligations = len(obligations)

    # If there are no obligations
    if total_obligations == 0:
        return {
            "contract_id": contract.id,
            "contract_number": contract.contract_number,
            "compliance_status": "Pending",
            "compliance_score": 0,
            "total_obligations": 0,
            "completed_obligations": 0,
            "pending_obligations": 0,
            "delayed_obligations": 0,
            "overdue_obligations": 0,
            "risk_level": "Low"
        }

    # Count obligation statuses
    completed = 0
    pending = 0
    delayed = 0
    overdue = 0

    for obligation in obligations:

        if obligation.status == "Completed":
            completed += 1

        elif obligation.status == "Pending":
            pending += 1

        elif obligation.status == "Delayed":
            delayed += 1

        elif obligation.status == "Overdue":
            overdue += 1

    # Compliance score
    compliance_score = (
        completed / total_obligations
    ) * 100

    # Determine compliance status
    if overdue >= 2:
        compliance_status = "Non-Compliant"

    elif overdue == 1:
        compliance_status = "Non-Compliant"

    elif delayed > 0:
        compliance_status = "Delayed"

    elif pending > 0:
        compliance_status = "Pending"

    elif completed == total_obligations:
        compliance_status = "Compliant"

    else:
        compliance_status = "Pending"

    # Determine risk level
    if overdue >= 2:
        risk_level = "High"

    elif overdue == 1:
        risk_level = "Medium"

    else:
        risk_level = "Low"

    return {
        "contract_id": contract.id,
        "contract_number": contract.contract_number,
        "compliance_status": compliance_status,
        "compliance_score": round(compliance_score, 2),
        "total_obligations": total_obligations,
        "completed_obligations": completed,
        "pending_obligations": pending,
        "delayed_obligations": delayed,
        "overdue_obligations": overdue,
        "risk_level": risk_level
    }