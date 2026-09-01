"""
Compliance evaluation logic (Sprint 11).

Rules (documented per section 15 requirement for an explainable business
rule rather than an opaque scoring model):

Compliance score = completed_obligations / total_obligations * 100
(a contract with zero obligations is treated as fully Compliant with a
score of 100, since there is nothing outstanding to violate.)

Compliance status:
  - No obligations, OR all obligations completed          -> Compliant
  - >=1 overdue obligation and it is the ONLY problem      -> Non-Compliant
  - >=1 delayed obligation (none overdue)                  -> Delayed
  - Only pending/in-progress obligations remain (no        -> Pending
    delayed/overdue)
  - 2 or more overdue obligations                          -> High Risk

Risk level (independent of the compliance status, used for the
high-risk endpoint and dashboards):
  - 0 overdue obligations       -> Low
  - 1 overdue obligation        -> Medium
  - >=2 overdue obligations     -> High
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.obligation import Obligation, ObligationStatus
from app.models.compliance import ComplianceRecord, ComplianceStatus, RiskLevel


@dataclass
class ComplianceResult:
    contract_id: int
    total_obligations: int
    completed_obligations: int
    pending_obligations: int
    in_progress_obligations: int
    delayed_obligations: int
    overdue_obligations: int
    compliance_score: float
    compliance_status: ComplianceStatus
    risk_level: RiskLevel


def evaluate_contract_compliance(db: Session, contract: Contract) -> ComplianceResult:
    obligations = db.query(Obligation).filter(Obligation.contract_id == contract.id).all()

    total = len(obligations)
    completed = sum(1 for o in obligations if o.status == ObligationStatus.COMPLETED)
    pending = sum(1 for o in obligations if o.status == ObligationStatus.PENDING)
    in_progress = sum(1 for o in obligations if o.status == ObligationStatus.IN_PROGRESS)
    delayed = sum(1 for o in obligations if o.status == ObligationStatus.DELAYED)
    # Treat both the explicit OVERDUE status and any non-completed obligation
    # whose due date has passed as "overdue" for evaluation purposes.
    overdue = sum(1 for o in obligations if o.status == ObligationStatus.OVERDUE or o.is_overdue)

    score = 100.0 if total == 0 else round((completed / total) * 100, 2)

    if total == 0 or completed == total:
        status = ComplianceStatus.COMPLIANT
    elif overdue >= 2:
        status = ComplianceStatus.HIGH_RISK
    elif overdue == 1:
        status = ComplianceStatus.NON_COMPLIANT
    elif delayed >= 1:
        status = ComplianceStatus.DELAYED
    else:
        status = ComplianceStatus.PENDING

    if overdue == 0:
        risk = RiskLevel.LOW
    elif overdue == 1:
        risk = RiskLevel.MEDIUM
    else:
        risk = RiskLevel.HIGH

    return ComplianceResult(
        contract_id=contract.id,
        total_obligations=total,
        completed_obligations=completed,
        pending_obligations=pending,
        in_progress_obligations=in_progress,
        delayed_obligations=delayed,
        overdue_obligations=overdue,
        compliance_score=score,
        compliance_status=status,
        risk_level=risk,
    )


def record_compliance_evaluation(db: Session, contract: Contract, result: ComplianceResult) -> ComplianceRecord:
    """Persist a history row for this evaluation (section 11 - Compliance History)."""
    record = ComplianceRecord(
        contract_id=contract.id,
        status=result.compliance_status,
        compliance_score=result.compliance_score,
        risk_level=result.risk_level,
        notes=(
            f"total={result.total_obligations}, completed={result.completed_obligations}, "
            f"overdue={result.overdue_obligations}, delayed={result.delayed_obligations}"
        ),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
