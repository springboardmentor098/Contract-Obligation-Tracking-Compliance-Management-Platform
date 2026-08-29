from datetime import datetime
import json

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.contract import Contract
from app.models.obligation import Obligation


def calculate_contract_compliance(
    db: Session,
    contract_id: int
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if contract is None:
        return None

    obligations = (
        db.query(Obligation)
        .filter(Obligation.contract_id == contract_id)
        .all()
    )

    total = len(obligations)

    completed = sum(
        1
        for obligation in obligations
        if obligation.status == "Completed"
    )

    pending = sum(
        1
        for obligation in obligations
        if obligation.status == "Pending"
    )

    overdue = sum(
        1
        for obligation in obligations
        if obligation.status == "Overdue"
    )

    in_progress = sum(
        1
        for obligation in obligations
        if obligation.status == "In Progress"
    )

    if total == 0:
        score = 0.0
        compliance_status = "Pending"
        risk_level = "Low"

    else:
        score = round(
            (completed / total) * 100,
            2
        )

        if overdue >= 2:
            compliance_status = "High Risk"
            risk_level = "High"

        elif overdue == 1:
            compliance_status = "Non-Compliant"
            risk_level = "Medium"

        elif completed == total:
            compliance_status = "Compliant"
            risk_level = "Low"

        elif in_progress > 0:
            compliance_status = "Delayed"
            risk_level = "Medium"

        else:
            compliance_status = "Pending"
            risk_level = "Low"

    return {
        "contract_id": contract.id,
        "compliance_status": compliance_status,
        "compliance_score": score,
        "total_obligations": total,
        "completed_obligations": completed,
        "pending_obligations": pending,
        "overdue_obligations": overdue,
        "risk_level": risk_level,
    }


def get_all_compliance(db: Session):
    contracts = (
        db.query(Contract)
        .order_by(Contract.id)
        .all()
    )

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
            "risk_level": compliance["risk_level"],
        })

    return results


def get_compliance_summary(db: Session):
    results = get_all_compliance(db)

    return {
        "total_contracts": len(results),

        "compliant_contracts": sum(
            1
            for item in results
            if item["compliance_status"] == "Compliant"
        ),

        "pending_contracts": sum(
            1
            for item in results
            if item["compliance_status"] == "Pending"
        ),

        "delayed_contracts": sum(
            1
            for item in results
            if item["compliance_status"] == "Delayed"
        ),

        "non_compliant_contracts": sum(
            1
            for item in results
            if item["compliance_status"] == "Non-Compliant"
        ),

        "high_risk_contracts": sum(
            1
            for item in results
            if item["compliance_status"] == "High Risk"
        ),
    }


def get_non_compliant_contracts(db: Session):
    results = get_all_compliance(db)

    return [
        item
        for item in results
        if item["compliance_status"] == "Non-Compliant"
    ]


def get_high_risk_contracts(db: Session):
    results = get_all_compliance(db)

    return [
        item
        for item in results
        if item["compliance_status"] == "High Risk"
    ]


# =========================================================
# COMPLIANCE HISTORY
# =========================================================

def save_compliance_history(
    db: Session,
    compliance: dict,
    user_id: int
):
    """
    Save a compliance evaluation in the existing audit_logs table.

    A new history record is created only when the current
    compliance result differs from the latest saved evaluation
    for the same contract.
    """

    latest_logs = (
        db.query(AuditLog)
        .filter(
            AuditLog.action == "COMPLIANCE_EVALUATED",
            AuditLog.entity_type == "Contract"
        )
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    history_data = {
        "contract_id": compliance["contract_id"],
        "compliance_status": compliance["compliance_status"],
        "compliance_score": compliance["compliance_score"],
        "total_obligations": compliance["total_obligations"],
        "completed_obligations": compliance["completed_obligations"],
        "pending_obligations": compliance["pending_obligations"],
        "overdue_obligations": compliance["overdue_obligations"],
        "risk_level": compliance["risk_level"],
    }

    # Check the latest evaluation for this contract.
    for log in latest_logs:
        try:
            previous_data = json.loads(log.details)

            if previous_data.get("contract_id") != compliance["contract_id"]:
                continue

            # Do not create duplicate history records
            # when the compliance result has not changed.
            if previous_data == history_data:
                return log

            break

        except (json.JSONDecodeError, TypeError):
            continue

    audit_log = AuditLog(
        user_id=user_id,
        action="COMPLIANCE_EVALUATED",
        entity_type="Contract",
        details=json.dumps(history_data),
        created_at=datetime.utcnow()
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log


def get_compliance_history(
    db: Session,
    contract_id: int
):
    """
    Return all saved compliance evaluations for a contract.
    """

    logs = (
        db.query(AuditLog)
        .filter(
            AuditLog.action == "COMPLIANCE_EVALUATED",
            AuditLog.entity_type == "Contract"
        )
        .order_by(AuditLog.created_at.desc())
        .all()
    )

    history = []

    for log in logs:
        try:
            data = json.loads(log.details)

            if data.get("contract_id") != contract_id:
                continue

            history.append({
                "id": log.id,
                "contract_id": contract_id,
                "compliance_status": data["compliance_status"],
                "compliance_score": data["compliance_score"],
                "total_obligations": data["total_obligations"],
                "completed_obligations": data["completed_obligations"],
                "pending_obligations": data["pending_obligations"],
                "overdue_obligations": data["overdue_obligations"],
                "risk_level": data["risk_level"],
                "evaluated_by": log.user_id,
                "evaluated_at": log.created_at,
            })

        except (json.JSONDecodeError, TypeError, KeyError):
            continue

    return history