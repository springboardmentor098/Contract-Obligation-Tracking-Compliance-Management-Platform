from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.report_service import (
    get_dashboard_summary,
    get_contract_summary,
    get_obligation_summary,
    get_renewal_summary,
    get_compliance_summary_report,
    get_risk_report,
)
from app.schemas.report import (
    DashboardSummaryResponse,
    ContractSummaryResponse,
    ObligationSummaryResponse,
    RenewalSummaryResponse,
    ComplianceSummaryResponse,
    RiskSummary,
)
from app.dependencies import get_current_user

router = APIRouter(
    tags=["Reports & Analytics"]
)


# =========================================================
# Dashboard Summary
# =========================================================

@router.get(
    "/dashboard/summary",
    response_model=DashboardSummaryResponse
)

def dashboard_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_dashboard_summary(db)


# =========================================================
# Contract Analytics
# =========================================================

@router.get(
    "/contracts/summary",
    response_model=ContractSummaryResponse
)
def contract_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_contract_summary(db)


# =========================================================
# Obligation Analytics
# =========================================================

@router.get(
    "/obligations/summary",
    response_model=ObligationSummaryResponse
)
def obligation_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_obligation_summary(db)


# =========================================================
# Renewal Analytics
# =========================================================

@router.get(
    "/renewals/summary",
    response_model=RenewalSummaryResponse
)
def renewal_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_renewal_summary(db)


# =========================================================
# Compliance Analytics
# =========================================================

@router.get(
    "/compliance/summary",
    response_model=ComplianceSummaryResponse
)
def compliance_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_compliance_summary_report(db)


# =========================================================
# Risk Analysis
# =========================================================

@router.get(
    "/risk",
    response_model=list[RiskSummary]
)
def risk_report(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_risk_report(db)