from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.obligation import Obligation


COMPLETED = "Completed"
PENDING = "Pending"
DELAYED = "Delayed"
OVERDUE = "Overdue"


def evaluate_contract_compliance(
    contract: Contract,
    db: Session,
):
    obligations = (
        db.query(Obligation)
        .filter(Obligation.contract_id == contract.id)
        .all()
    )

    total = len(obligations)

    if total == 0:
        return {
            "contract_id": contract.id,
            "compliance_status": "Pending",
            "compliance_score": 0,
            "total_obligations": 0,
            "completed_obligations": 0,
            "pending_obligations": 0,
            "delayed_obligations": 0,
            "overdue_obligations": 0,
            "risk_level": "Low",
        }

    completed = sum(
        1 for obligation in obligations
        if obligation.status == COMPLETED
    )

    pending = sum(
        1 for obligation in obligations
        if obligation.status == PENDING
    )

    delayed = sum(
        1 for obligation in obligations
        if obligation.status == DELAYED
    )

    overdue = sum(
        1 for obligation in obligations
        if obligation.status == OVERDUE
    )

    compliance_score = round(
        (completed / total) * 100,
        2,
    )

    if overdue >= 2:
        risk_level = "High"
    elif overdue == 1:
        risk_level = "Medium"
    else:
        risk_level = "Low"

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

    return {
        "contract_id": contract.id,
        "compliance_status": compliance_status,
        "compliance_score": compliance_score,
        "total_obligations": total,
        "completed_obligations": completed,
        "pending_obligations": pending,
        "delayed_obligations": delayed,
        "overdue_obligations": overdue,
        "risk_level": risk_level,
    }


def get_all_contract_compliance(
    db: Session,
):
    contracts = db.query(Contract).all()

    results = []

    for contract in contracts:
        compliance = evaluate_contract_compliance(
            contract,
            db,
        )

        results.append(
            {
                **compliance,
                "contract_number": contract.contract_number,
            }
        )

    return results
