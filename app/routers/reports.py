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
    generate_contract_pdf,
    generate_obligation_pdf,
    generate_renewal_pdf,
    generate_compliance_pdf,
    generate_contract_excel,
    generate_obligation_excel,
    generate_renewal_excel,
    generate_compliance_excel,
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
from fastapi.responses import StreamingResponse

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

# =========================================================
# PDF EXPORTS
# =========================================================


# ---------------------------------------------------------
# CONTRACT PDF
# GET /reports/contracts/export/pdf
# ---------------------------------------------------------

@router.get(
    "/contracts/export/pdf",
    operation_id="export_contract_report_pdf"
)
def export_contract_report_pdf(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    pdf_file = generate_contract_pdf(db)

    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=contract_report.pdf"
        }
    )


# ---------------------------------------------------------
# OBLIGATION PDF
# GET /reports/obligations/export/pdf
# ---------------------------------------------------------

@router.get(
    "/obligations/export/pdf",
    operation_id="export_obligation_report_pdf"
)
def export_obligation_report_pdf(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    pdf_file = generate_obligation_pdf(db)

    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=obligation_report.pdf"
        }
    )


# ---------------------------------------------------------
# RENEWAL PDF
# GET /reports/renewals/export/pdf
# ---------------------------------------------------------

@router.get(
    "/renewals/export/pdf",
    operation_id="export_renewal_report_pdf"
)
def export_renewal_report_pdf(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    pdf_file = generate_renewal_pdf(db)

    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=renewal_report.pdf"
        }
    )


# ---------------------------------------------------------
# COMPLIANCE PDF
# GET /reports/compliance/export/pdf
# ---------------------------------------------------------

@router.get(
    "/compliance/export/pdf",
    operation_id="export_compliance_report_pdf"
)
def export_compliance_report_pdf(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    pdf_file = generate_compliance_pdf(db)

    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=compliance_report.pdf"
        }
    )
# =========================================================
# EXCEL EXPORTS
# =========================================================


@router.get(
    "/contracts/export/excel",
    operation_id="export_contract_report_excel"
)
def export_contract_report_excel(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    excel_file = generate_contract_excel(db)

    return StreamingResponse(
        excel_file,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=contract_report.xlsx"
        }
    )


@router.get(
    "/obligations/export/excel",
    operation_id="export_obligation_report_excel"
)
def export_obligation_report_excel(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    excel_file = generate_obligation_excel(db)

    return StreamingResponse(
        excel_file,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=obligation_report.xlsx"
        }
    )


@router.get(
    "/renewals/export/excel",
    operation_id="export_renewal_report_excel"
)
def export_renewal_report_excel(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    excel_file = generate_renewal_excel(db)

    return StreamingResponse(
        excel_file,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=renewal_report.xlsx"
        }
    )


@router.get(
    "/compliance/export/excel",
    operation_id="export_compliance_report_excel"
)
def export_compliance_report_excel(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    excel_file = generate_compliance_excel(db)

    return StreamingResponse(
        excel_file,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=compliance_report.xlsx"
        }
    )