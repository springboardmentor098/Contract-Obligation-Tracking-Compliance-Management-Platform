from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.contract import Contract
from app.models.compliance import ComplianceStatus, RiskLevel
from app.schemas.compliance import (
    ComplianceListItem,
    ComplianceSummary,
    NonCompliantContract,
    HighRiskContract,
)
from app.core.deps import get_current_active_user
from app.core.permissions import require_roles, COMPLIANCE_VIEW_ROLES
from app.services.compliance_service import evaluate_contract_compliance
from app.services.notification_service import notify_compliance_alert

router = APIRouter(prefix="/compliance", tags=["Compliance"])

# NOTE: FastAPI matches routes in declaration order, so the fixed-path routes
# (/compliance/summary, /compliance/non-compliant, /compliance/high-risk)
# are registered before the generic /contracts/{contract_id}/compliance route
# to avoid "high-risk" etc. being interpreted as a contract_id.


@router.get("/summary", response_model=ComplianceSummary)
def get_compliance_summary(
    current_user: User = Depends(require_roles(*COMPLIANCE_VIEW_ROLES)),
    db: Session = Depends(get_db),
):
    contracts = db.query(Contract).all()
    counts = {status_: 0 for status_ in ComplianceStatus}
    for contract in contracts:
        result = evaluate_contract_compliance(db, contract)
        counts[result.compliance_status] += 1

    return ComplianceSummary(
        total_contracts=len(contracts),
        compliant_contracts=counts[ComplianceStatus.COMPLIANT],
        pending_contracts=counts[ComplianceStatus.PENDING],
        delayed_contracts=counts[ComplianceStatus.DELAYED],
        non_compliant_contracts=counts[ComplianceStatus.NON_COMPLIANT],
        high_risk_contracts=counts[ComplianceStatus.HIGH_RISK],
    )


@router.get("/non-compliant", response_model=List[NonCompliantContract])
def get_non_compliant_contracts(
    current_user: User = Depends(require_roles(*COMPLIANCE_VIEW_ROLES)),
    db: Session = Depends(get_db),
):
    results = []
    for contract in db.query(Contract).all():
        result = evaluate_contract_compliance(db, contract)
        if result.compliance_status in (ComplianceStatus.NON_COMPLIANT, ComplianceStatus.HIGH_RISK):
            results.append(
                NonCompliantContract(
                    contract_id=contract.id,
                    contract_number=contract.contract_number,
                    compliance_status=result.compliance_status,
                    overdue_obligations=result.overdue_obligations,
                )
            )
    return results


@router.get("/high-risk", response_model=List[HighRiskContract])
def get_high_risk_contracts(
    current_user: User = Depends(require_roles(*COMPLIANCE_VIEW_ROLES)),
    db: Session = Depends(get_db),
):
    results = []
    for contract in db.query(Contract).all():
        result = evaluate_contract_compliance(db, contract)
        if result.risk_level == RiskLevel.HIGH:
            results.append(
                HighRiskContract(
                    contract_id=contract.id,
                    contract_number=contract.contract_number,
                    risk_level=result.risk_level,
                    overdue_obligations=result.overdue_obligations,
                )
            )
            compliance_officers = [
                u.id for u in db.query(User).filter(User.role == UserRole.COMPLIANCE_OFFICER).all()
            ]
            notify_compliance_alert(
                db,
                contract,
                compliance_officers,
                f"Contract {contract.contract_number} has {result.overdue_obligations} overdue obligations "
                "and requires immediate attention.",
            )
    return results


@router.get("", response_model=List[ComplianceListItem])
def list_all_compliance(
    current_user: User = Depends(require_roles(*COMPLIANCE_VIEW_ROLES)),
    db: Session = Depends(get_db),
):
    items = []
    for contract in db.query(Contract).all():
        result = evaluate_contract_compliance(db, contract)
        items.append(
            ComplianceListItem(
                contract_id=contract.id,
                contract_number=contract.contract_number,
                compliance_status=result.compliance_status,
                compliance_score=result.compliance_score,
            )
        )
    return items
