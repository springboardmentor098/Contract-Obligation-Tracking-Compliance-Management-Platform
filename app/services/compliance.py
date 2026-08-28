from sqlalchemy.orm import Session

from app.models.contracts import Contract
from app.models.obligations import Obligation


def calculate_contract_compliance(
    db: Session,
    contract_id: int
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        return None

    obligations = db.query(Obligation).filter(
        Obligation.contract_id == contract_id
    ).all()

    total = len(obligations)

    if total == 0:
        return {
            "contract_id": contract_id,
            "compliance_status": "Pending",
            "compliance_score": 0,
            "total_obligations": 0,
            "completed_obligations": 0,
            "pending_obligations": 0,
            "delayed_obligations": 0,
            "overdue_obligations": 0,
            "risk_level": "Low"
        }

    completed = sum(
        1 for o in obligations
        if o.status == "Completed"
    )

    pending = sum(
        1 for o in obligations
        if o.status == "Pending"
    )

    delayed = sum(
        1 for o in obligations
        if o.status == "Delayed"
    )

    overdue = sum(
        1 for o in obligations
        if o.status == "Overdue"
    )

    compliance_score = round(
        (completed / total) * 100,
        2
    )

    # Compliance status
    if overdue > 0:
        compliance_status = "Non-Compliant"
    elif delayed > 0:
        compliance_status = "Delayed"
    elif pending > 0:
        compliance_status = "Pending"
    elif completed == total:
        compliance_status = "Compliant"
    else:
        compliance_status = "Pending"

    # Risk level
    if overdue >= 2:
        risk_level = "High"
    elif overdue == 1:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "contract_id": contract_id,
        "compliance_status": compliance_status,
        "compliance_score": compliance_score,
        "total_obligations": total,
        "completed_obligations": completed,
        "pending_obligations": pending,
        "delayed_obligations": delayed,
        "overdue_obligations": overdue,
        "risk_level": risk_level
    }


def get_all_compliance(db: Session):
    contracts = db.query(Contract).all()

    results = []

    for contract in contracts:
        compliance = calculate_contract_compliance(
            db,
            contract.id
        )

        results.append({
            "contract_id": contract.id,
            "contract_number": contract.contract_number,
            "compliance_status": compliance["compliance_status"],
            "compliance_score": compliance["compliance_score"],
            "overdue_obligations": compliance["overdue_obligations"],
            "risk_level": compliance["risk_level"]
        })

    return results


def get_compliance_summary(db: Session):
    records = get_all_compliance(db)

    return {
        "total_contracts": len(records),
        "compliant_contracts": sum(
            1 for r in records
            if r["compliance_status"] == "Compliant"
        ),
        "pending_contracts": sum(
            1 for r in records
            if r["compliance_status"] == "Pending"
        ),
        "delayed_contracts": sum(
            1 for r in records
            if r["compliance_status"] == "Delayed"
        ),
        "non_compliant_contracts": sum(
            1 for r in records
            if r["compliance_status"] == "Non-Compliant"
        ),
        "high_risk_contracts": sum(
            1 for r in records
            if r["risk_level"] == "High"
        )
    }


def get_non_compliant_contracts(db: Session):
    records = get_all_compliance(db)

    return [
        r for r in records
        if r["compliance_status"] == "Non-Compliant"
    ]


def get_high_risk_contracts(db: Session):
    records = get_all_compliance(db)

    return [
        r for r in records
        if r["risk_level"] == "High"
    ]