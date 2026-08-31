from datetime import date

from sqlalchemy.orm import Session

from app.models.obligation import Obligation


def calculate_contract_compliance(
    contract_id: int,
    db: Session
):
    obligations = (
        db.query(Obligation)
        .filter(Obligation.contract_id == contract_id)
        .all()
    )

    total_obligations = len(obligations)

    if total_obligations == 0:
        return {
            "compliance_status": "Pending",
            "compliance_score": 0,
            "total_obligations": 0,
            "completed_obligations": 0,
            "pending_obligations": 0,
            "delayed_obligations": 0,
            "overdue_obligations": 0,
            "risk_level": "Low"
        }

    today = date.today()

    completed = 0
    pending = 0
    delayed = 0
    overdue = 0

    for obligation in obligations:

        if obligation.status == "Completed":
            completed += 1

        elif obligation.status == "Delayed":
            delayed += 1

        elif (
            obligation.status == "Pending"
            and obligation.due_date < today
        ):
            overdue += 1

        else:
            pending += 1

    compliance_score = round(
        (completed / total_obligations) * 100
    )

    # Determine risk
    if overdue >= 2:
        risk_level = "High"
    elif overdue == 1:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    # Determine compliance status
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
        "compliance_status": compliance_status,
        "compliance_score": compliance_score,
        "total_obligations": total_obligations,
        "completed_obligations": completed,
        "pending_obligations": pending,
        "delayed_obligations": delayed,
        "overdue_obligations": overdue,
        "risk_level": risk_level
    }