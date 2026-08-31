from datetime import date

from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.obligation import Obligation


def calculate_compliance(
    contract: Contract,
    db: Session
):
    obligations = db.query(Obligation).filter(
        Obligation.contract_id == contract.id
    ).all()

    total_obligations = len(obligations)

    completed_obligations = sum(
        1 for obligation in obligations
        if obligation.status == "Completed"
    )

    pending_obligations = sum(
        1 for obligation in obligations
        if obligation.status == "Pending"
    )

    delayed_obligations = sum(
        1 for obligation in obligations
        if obligation.status == "Delayed"
    )

    overdue_obligations = sum(
        1 for obligation in obligations
        if (
            obligation.status == "Overdue"
            or (
                obligation.due_date < date.today()
                and obligation.status != "Completed"
            )
        )
    )

    if total_obligations == 0:
        compliance_score = 0
    else:
        compliance_score = (
            completed_obligations / total_obligations
        ) * 100

    # Compliance status
    if overdue_obligations >= 3:
        compliance_status = "High Risk"
    elif overdue_obligations > 0:
        compliance_status = "Non-Compliant"
    elif delayed_obligations > 0:
        compliance_status = "Delayed"
    elif pending_obligations > 0:
        compliance_status = "Pending"
    else:
        compliance_status = "Compliant"

    # Risk level
    if overdue_obligations >= 3:
        risk_level = "High"
    elif overdue_obligations == 1 or overdue_obligations == 2:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "contract_id": contract.id,
        "compliance_status": compliance_status,
        "compliance_score": compliance_score,
        "total_obligations": total_obligations,
        "completed_obligations": completed_obligations,
        "pending_obligations": pending_obligations,
        "overdue_obligations": overdue_obligations,
        "risk_level": risk_level
    }


def get_all_compliance(
    db: Session
):
    contracts = db.query(Contract).all()

    results = []

    for contract in contracts:
        compliance = calculate_compliance(
            contract,
            db
        )

        results.append({
            "contract_id": contract.id,
            "contract_number": contract.contract_number,
            "compliance_status": compliance["compliance_status"],
            "compliance_score": compliance["compliance_score"]
        })

    return results


def get_compliance_summary(
    db: Session
):
    contracts = db.query(Contract).all()

    summary = {
        "total_contracts": len(contracts),
        "compliant_contracts": 0,
        "pending_contracts": 0,
        "delayed_contracts": 0,
        "non_compliant_contracts": 0,
        "high_risk_contracts": 0
    }

    for contract in contracts:
        compliance = calculate_compliance(
            contract,
            db
        )

        compliance_status = compliance["compliance_status"]

        if compliance_status == "Compliant":
            summary["compliant_contracts"] += 1

        elif compliance_status == "Pending":
            summary["pending_contracts"] += 1

        elif compliance_status == "Delayed":
            summary["delayed_contracts"] += 1

        elif compliance_status == "Non-Compliant":
            summary["non_compliant_contracts"] += 1

        elif compliance_status == "High Risk":
            summary["high_risk_contracts"] += 1

    return summary


def get_non_compliant_contracts(
    db: Session
):
    contracts = db.query(Contract).all()

    results = []

    for contract in contracts:
        compliance = calculate_compliance(
            contract,
            db
        )

        if compliance["compliance_status"] in [
            "Non-Compliant",
            "High Risk"
        ]:
            results.append({
                "contract_id": contract.id,
                "contract_number": contract.contract_number,
                "compliance_status": compliance[
                    "compliance_status"
                ],
                "overdue_obligations": compliance[
                    "overdue_obligations"
                ]
            })

    return results


def get_high_risk_contracts(
    db: Session
):
    contracts = db.query(Contract).all()

    results = []

    for contract in contracts:
        compliance = calculate_compliance(
            contract,
            db
        )

        if compliance["risk_level"] == "High":
            results.append({
                "contract_id": contract.id,
                "contract_number": contract.contract_number,
                "risk_level": compliance["risk_level"],
                "overdue_obligations": compliance[
                    "overdue_obligations"
                ]
            })

    return results