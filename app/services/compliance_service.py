from datetime import date

from sqlalchemy.orm import Session

from app.models.obligation import Obligation


def calculate_contract_compliance(
    db: Session,
    contract_id: int
):
    obligations = db.query(Obligation).filter(
        Obligation.contract_id == contract_id
    ).all()

    total_obligations = len(obligations)

    if total_obligations == 0:
        return {
            "contract_id": contract_id,
            "total_obligations": 0,
            "completed_obligations": 0,
            "pending_obligations": 0,
            "overdue_obligations": 0,
            "compliance_score": 0,
            "compliance_status": "No Obligations",
            "risk_level": "Low"
        }

    today = date.today()

    completed = 0
    pending = 0
    overdue = 0

    for obligation in obligations:

        if obligation.status == "Completed":
            completed += 1

        elif (
            obligation.due_date < today
            and obligation.status != "Completed"
        ):
            overdue += 1

        else:
            pending += 1

    compliance_score = round(
        (completed / total_obligations) * 100,
        2
    )

    if overdue >= 2:
        risk_level = "High"
    elif overdue == 1:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    if compliance_score == 100 and overdue == 0:
        compliance_status = "Compliant"
    elif compliance_score > 0:
        compliance_status = "Partially Compliant"
    else:
        compliance_status = "Non-Compliant"

    return {
        "contract_id": contract_id,
        "total_obligations": total_obligations,
        "completed_obligations": completed,
        "pending_obligations": pending,
        "overdue_obligations": overdue,
        "compliance_score": compliance_score,
        "compliance_status": compliance_status,
        "risk_level": risk_level
    }