from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models.contract import Contract, ContractStatus
from app.models.obligation import Obligation, ObligationStatus
from app.models.renewal import Renewal, RenewalStatus
from app.models.compliance import ComplianceStatus, RiskLevel
from app.services.compliance_service import evaluate_contract_compliance

UPCOMING_RENEWAL_DAYS = 30


def _enum_counts(values, enum_cls):
    counts = {item.value: 0 for item in enum_cls}
    for value in values:
        counts[value.value] += 1
    return counts


def contract_summary(db: Session) -> dict[str, Any]:
    contracts = db.query(Contract).all()
    counts = _enum_counts((c.status for c in contracts), ContractStatus)
    categories: dict[str, int] = {}
    for contract in contracts:
        key = contract.category.value
        categories[key] = categories.get(key, 0) + 1
    return {
        "total": len(contracts),
        "active": counts[ContractStatus.ACTIVE.value],
        "draft": counts[ContractStatus.DRAFT.value],
        "under_review": counts[ContractStatus.UNDER_REVIEW.value],
        "approved": counts[ContractStatus.APPROVED.value],
        "expired": counts[ContractStatus.EXPIRED.value],
        "terminated": counts[ContractStatus.TERMINATED.value],
        "by_category": categories,
    }


def obligation_summary(db: Session) -> dict[str, Any]:
    obligations = db.query(Obligation).all()
    effective = []
    for obligation in obligations:
        status = obligation.status
        if status != ObligationStatus.COMPLETED and obligation.due_date < date.today():
            status = ObligationStatus.OVERDUE
        effective.append(status)
    counts = _enum_counts(effective, ObligationStatus)
    return {
        "total": len(obligations),
        "pending": counts[ObligationStatus.PENDING.value],
        "in_progress": counts[ObligationStatus.IN_PROGRESS.value],
        "completed": counts[ObligationStatus.COMPLETED.value],
        "delayed": counts[ObligationStatus.DELAYED.value],
        "overdue": counts[ObligationStatus.OVERDUE.value],
    }


def overdue_obligations(db: Session) -> list[dict[str, Any]]:
    today = date.today()
    rows = []
    for o in db.query(Obligation).filter(Obligation.status != ObligationStatus.COMPLETED).all():
        if o.due_date < today:
            rows.append({
                "obligation_id": o.id,
                "contract_id": o.contract_id,
                "title": o.title,
                "due_date": o.due_date,
                "days_overdue": (today - o.due_date).days,
                "status": ObligationStatus.OVERDUE.value,
            })
    return sorted(rows, key=lambda x: x["due_date"])


def renewal_summary(db: Session, upcoming_days: int = UPCOMING_RENEWAL_DAYS) -> dict[str, Any]:
    renewals = db.query(Renewal).all()
    counts = _enum_counts((r.status for r in renewals), RenewalStatus)
    today = date.today()
    cutoff = today + timedelta(days=upcoming_days)
    upcoming = [r for r in renewals if r.status == RenewalStatus.UPCOMING and today <= r.renewal_date <= cutoff]
    approaching = []
    for contract in db.query(Contract).all():
        if today <= contract.end_date <= cutoff:
            approaching.append({
                "contract_id": contract.id,
                "contract_number": contract.contract_number,
                "contract_title": contract.title,
                "expiry_date": contract.end_date,
                "days_remaining": (contract.end_date - today).days,
            })
    approaching.sort(key=lambda x: x["expiry_date"])
    return {
        "upcoming": len(upcoming),
        "in_progress": counts[RenewalStatus.IN_PROGRESS.value],
        "renewed": counts[RenewalStatus.RENEWED.value],
        "expired": counts[RenewalStatus.EXPIRED.value],
        "cancelled": counts[RenewalStatus.CANCELLED.value],
        "upcoming_days": upcoming_days,
        "approaching_expiry": approaching,
    }


def compliance_summary(db: Session) -> dict[str, Any]:
    contracts = db.query(Contract).all()
    counts = {item.value: 0 for item in ComplianceStatus}
    risk_counts = {item.value: 0 for item in RiskLevel}
    evaluations = []
    for contract in contracts:
        result = evaluate_contract_compliance(db, contract)
        counts[result.compliance_status.value] += 1
        risk_counts[result.risk_level.value] += 1
        evaluations.append((contract, result))
    return {
        "total_contracts_evaluated": len(contracts),
        "compliant": counts[ComplianceStatus.COMPLIANT.value],
        "pending": counts[ComplianceStatus.PENDING.value],
        "delayed": counts[ComplianceStatus.DELAYED.value],
        "non_compliant": counts[ComplianceStatus.NON_COMPLIANT.value],
        "high_risk": counts[ComplianceStatus.HIGH_RISK.value],
        "risk_indicators": {
            "low": risk_counts[RiskLevel.LOW.value],
            "medium": risk_counts[RiskLevel.MEDIUM.value],
            "high": risk_counts[RiskLevel.HIGH.value],
        },
        "high_risk_contracts": [
            {
                "contract_id": contract.id,
                "contract_number": contract.contract_number,
                "contract_title": contract.title,
                "risk_level": result.risk_level.value,
                "compliance_status": result.compliance_status.value,
                "compliance_score": result.compliance_score,
                "overdue_obligations": result.overdue_obligations,
            }
            for contract, result in evaluations if result.risk_level == RiskLevel.HIGH
        ],
    }


def risk_summary(db: Session) -> dict[str, Any]:
    compliance = compliance_summary(db)
    return {
        "risk_indicators": compliance["risk_indicators"],
        "high_risk_contracts": compliance["high_risk_contracts"],
    }


def dashboard_summary(db: Session) -> dict[str, Any]:
    return {
        "contracts": contract_summary(db),
        "obligations": obligation_summary(db),
        "renewals": renewal_summary(db),
        "compliance": compliance_summary(db),
    }
