from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

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


# =========================================================
# REPORTS ROUTER
# =========================================================

router = APIRouter(
    prefix="/reports",
    tags=["Reports & Analytics"]
)


# =========================================================
# DASHBOARD ROUTER
# =========================================================

dashboard_router = APIRouter(
    tags=["Dashboard"]
)


# =========================================================
# DASHBOARD SUMMARY
# GET /dashboard/summary
# =========================================================

@dashboard_router.get(
    "/dashboard/summary",
    response_model=DashboardSummaryResponse,
    operation_id="dashboard_summary"
)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return get_dashboard_summary(db)


# =========================================================
# CONTRACT SUMMARY
# GET /reports/contracts/summary
# =========================================================

@router.get(
    "/contracts/summary",
    response_model=ContractSummaryResponse,
    operation_id="reports_contract_summary"
)
def contract_summary(
    status: str | None = Query(
        default=None,
        description=(
            "Optional contract status filter. "
            "Example: Active, Draft, Under Review, "
            "Approved, Expired, Terminated"
        )
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return get_contract_summary(
        db,
        status=status
    )


# =========================================================
# OBLIGATION SUMMARY
# GET /reports/obligations/summary
# =========================================================

@router.get(
    "/obligations/summary",
    response_model=ObligationSummaryResponse,
    operation_id="reports_obligation_summary"
)
def obligation_summary(
    status: str | None = Query(
        default=None,
        description=(
            "Optional obligation status filter. "
            "Example: Pending, In Progress, "
            "Completed, Delayed"
        )
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return get_obligation_summary(
        db,
        status=status
    )


# =========================================================
# RENEWAL SUMMARY
# GET /reports/renewals/summary
# =========================================================

@router.get(
    "/renewals/summary",
    response_model=RenewalSummaryResponse,
    operation_id="reports_renewal_summary"
)
def renewal_summary(
    start_date: date | None = Query(
        default=None,
        description="Start date for renewal-date filtering"
    ),
    end_date: date | None = Query(
        default=None,
        description="End date for renewal-date filtering"
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if start_date and end_date:

        if start_date > end_date:

            raise HTTPException(
                status_code=400,
                detail=(
                    "start_date cannot be later "
                    "than end_date"
                )
            )

    return get_renewal_summary(
        db,
        start_date=start_date,
        end_date=end_date
    )


# =========================================================
# COMPLIANCE SUMMARY
# GET /reports/compliance/summary
# =========================================================

@router.get(
    "/compliance/summary",
    response_model=ComplianceSummaryResponse,
    operation_id="reports_compliance_summary"
)
def compliance_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return get_compliance_summary_report(db)


# =========================================================
# RISK ANALYSIS
# GET /reports/risk
# =========================================================

@router.get(
    "/risk",
    response_model=list[RiskSummary],
    operation_id="reports_risk"
)
def risk_report(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return get_risk_report(db)