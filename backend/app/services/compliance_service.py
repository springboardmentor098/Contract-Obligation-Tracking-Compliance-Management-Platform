from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.compliance import Compliance


def get_upcoming_obligations(
    db: Session,
    days: int = 30,
):
    today = date.today()
    limit_date = today + timedelta(days=days)

    return db.execute(
        select(Obligation)
        .where(
            Obligation.due_date.is_not(None),
            Obligation.due_date >= today,
            Obligation.due_date <= limit_date,
            Obligation.status != "Completed",
        )
        .order_by(Obligation.due_date)
    ).scalars().all()


def get_expiring_contracts(
    db: Session,
    days: int = 30,
):
    today = date.today()
    limit_date = today + timedelta(days=days)

    return db.execute(
        select(Contract)
        .where(
            Contract.end_date.is_not(None),
            Contract.end_date >= today,
            Contract.end_date <= limit_date,
            Contract.status != "Expired",
        )
        .order_by(Contract.end_date)
    ).scalars().all()


def calculate_contract_compliance(
    db: Session,
    contract_id: UUID,
) -> Compliance:
    contract = db.get(Contract, contract_id)

    if not contract:
        raise ValueError("Contract not found")

    obligations = db.execute(
        select(Obligation)
        .where(
            Obligation.contract_id == contract_id,
        )
    ).scalars().all()

    today = date.today()

    total = len(obligations)
    completed = 0
    pending = 0
    overdue = 0
    delayed = 0

    for obligation in obligations:
        status_value = (obligation.status or "Pending").lower()

        if status_value == "completed":
            completed += 1
            continue

        pending += 1

        if obligation.due_date and obligation.due_date < today:
            overdue += 1

        if (
            obligation.due_date
            and obligation.due_date < today
            and status_value in {"delayed", "overdue"}
        ):
            delayed += 1

    if total == 0:
        compliance_score = 100
    else:
        compliance_score = round((completed / total) * 100)

    if compliance_score >= 80:
        compliance_status = "Compliant"
    elif compliance_score >= 50:
        compliance_status = "Partially Compliant"
    else:
        compliance_status = "Non-Compliant"

    if overdue > 0 or delayed > 0:
        risk_level = "High"
    elif pending > 0:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    notes = (
        f"Compliance evaluated for contract {contract.contract_number}. "
        f"{completed} of {total} obligations completed."
    )

    compliance = db.execute(
        select(Compliance)
        .where(
            Compliance.contract_id == contract_id,
        )
        .order_by(Compliance.evaluated_at.desc())
    ).scalars().first()

    if compliance is None:
        compliance = Compliance(
            contract_id=contract_id,
        )
        db.add(compliance)

    compliance.compliance_score = compliance_score
    compliance.total_obligations = total
    compliance.completed_obligations = completed
    compliance.pending_obligations = pending
    compliance.overdue_obligations = overdue
    compliance.delayed_obligations = delayed
    compliance.compliance_status = compliance_status
    compliance.risk_level = risk_level
    compliance.notes = notes

    db.commit()
    db.refresh(compliance)

    return compliance


def get_contract_compliance(
    db: Session,
    contract_id: UUID,
) -> Compliance | None:
    return db.execute(
        select(Compliance)
        .where(
            Compliance.contract_id == contract_id,
        )
        .order_by(Compliance.evaluated_at.desc())
    ).scalars().first()


def get_compliance_summary(
    db: Session,
):
    records = db.execute(
        select(Compliance)
    ).scalars().all()

    total_contracts = len(records)

    compliant_contracts = sum(
        1
        for record in records
        if record.compliance_status == "Compliant"
    )

    non_compliant_contracts = sum(
        1
        for record in records
        if record.compliance_status == "Non-Compliant"
    )

    high_risk_contracts = sum(
        1
        for record in records
        if record.risk_level == "High"
    )

    if total_contracts == 0:
        average_compliance_score = 0.0
    else:
        average_compliance_score = round(
            sum(record.compliance_score for record in records)
            / total_contracts,
            2,
        )

    return {
        "total_contracts": total_contracts,
        "compliant_contracts": compliant_contracts,
        "non_compliant_contracts": non_compliant_contracts,
        "high_risk_contracts": high_risk_contracts,
        "average_compliance_score": average_compliance_score,
    }