from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.security import get_current_user

from app.schemas.report import (
    ContractSummaryResponse,
    ObligationSummaryResponse,
    RenewalSummaryResponse,
    ComplianceSummaryResponse,
    DashboardSummaryResponse,
)

from app.services.report_service import (
    get_contract_summary,
    get_obligation_summary,
    get_renewal_summary,
    get_compliance_summary,
    get_dashboard_summary,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports & Analytics"],
)


# ============================================================
# CONTRACT REPORT
# GET /reports/contracts
# ============================================================

@router.get(
    "/contracts",
    response_model=ContractSummaryResponse,
)
def contract_summary(
    status: Optional[str] = Query(
        default=None,
        description="Filter contracts by status",
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_contract_summary(
        db=db,
        status=status,
    )


# ============================================================
# OBLIGATION REPORT
# GET /reports/obligations
# ============================================================

@router.get(
    "/obligations",
    response_model=ObligationSummaryResponse,
)
def obligation_summary(
    status: Optional[str] = Query(
        default=None,
        description="Filter obligations by status",
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_obligation_summary(
        db=db,
        status=status,
    )


# ============================================================
# RENEWAL REPORT
# GET /reports/renewals
# ============================================================

@router.get(
    "/renewals",
    response_model=RenewalSummaryResponse,
)
def renewal_summary(
    start_date: Optional[date] = Query(
        default=None,
        description="Start date for renewal filtering",
    ),
    end_date: Optional[date] = Query(
        default=None,
        description="End date for renewal filtering",
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date cannot be after end_date",
        )

    return get_renewal_summary(
        db=db,
        start_date=start_date,
        end_date=end_date,
    )


# ============================================================
# COMPLIANCE REPORT
# GET /reports/compliance
# ============================================================

@router.get(
    "/compliance",
    response_model=ComplianceSummaryResponse,
)
def compliance_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_compliance_summary(db)


# ============================================================
# DASHBOARD SUMMARY
# GET /reports/dashboard
# ============================================================

@router.get(
    "/dashboard",
    response_model=DashboardSummaryResponse,
)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_dashboard_summary(db)
