from datetime import date

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User

from app.schemas.report import (
    DashboardSummaryResponse,
    ContractSummaryResponse,
    ObligationSummaryResponse,
    RenewalSummaryResponse,
    ComplianceSummaryResponse,
    RiskSummaryResponse,
    ContractReportResponse,
    ObligationReportResponse,
    RenewalReportResponse,
    ComplianceReportResponse,
)

from app.services.report_service import (
    get_dashboard_summary,
    get_contract_summary,
    get_obligation_summary,
    get_renewal_summary,
    get_compliance_report_summary,
    get_risk_summary,
    generate_contract_report,
    generate_obligation_report,
    generate_renewal_report,
    generate_compliance_report,
    generate_pdf_report,
    generate_excel_report,
)


router = APIRouter(tags=["Reports"])


# =========================================================
# DASHBOARD SUMMARY
# GET /dashboard/summary
# =========================================================

@router.get(
    "/dashboard/summary",
    response_model=DashboardSummaryResponse
)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_dashboard_summary(
        db,
        current_user
    )


# =========================================================
# CONTRACT ANALYTICS
# GET /reports/contracts/summary
# =========================================================

@router.get(
    "/reports/contracts/summary",
    response_model=ContractSummaryResponse
)
def contract_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_contract_summary(
        db,
        current_user
    )


# =========================================================
# OBLIGATION ANALYTICS
# GET /reports/obligations/summary
# =========================================================

@router.get(
    "/reports/obligations/summary",
    response_model=ObligationSummaryResponse
)
def obligation_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_obligation_summary(
        db,
        current_user
    )


# =========================================================
# RENEWAL ANALYTICS
# GET /reports/renewals/summary
# =========================================================

@router.get(
    "/reports/renewals/summary",
    response_model=RenewalSummaryResponse
)
def renewal_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_renewal_summary(
        db,
        current_user
    )


# =========================================================
# COMPLIANCE ANALYTICS
# GET /reports/compliance/summary
# =========================================================

@router.get(
    "/reports/compliance/summary",
    response_model=ComplianceSummaryResponse
)
def compliance_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_compliance_report_summary(
        db,
        current_user
    )


# =========================================================
# RISK ANALYTICS
# GET /reports/risk
# =========================================================

@router.get(
    "/reports/risk",
    response_model=RiskSummaryResponse
)
def risk_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_risk_summary(
        db,
        current_user
    )


# =========================================================
# CONTRACT REPORT
# GET /reports/contracts
# =========================================================

@router.get(
    "/reports/contracts",
    response_model=ContractReportResponse
)
def contract_report(
    status: str | None = Query(
        default=None,
        description="Filter contracts by status"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return generate_contract_report(
        db,
        current_user,
        status
    )


# =========================================================
# OBLIGATION REPORT
# GET /reports/obligations
# =========================================================

@router.get(
    "/reports/obligations",
    response_model=ObligationReportResponse
)
def obligation_report(
    status: str | None = Query(
        default=None,
        description="Filter obligations by status"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return generate_obligation_report(
        db,
        current_user,
        status
    )


# =========================================================
# RENEWAL REPORT
# GET /reports/renewals
# =========================================================

@router.get(
    "/reports/renewals",
    response_model=RenewalReportResponse
)
def renewal_report(
    status: str | None = Query(
        default=None,
        description="Filter renewals by status"
    ),
    start_date: date | None = Query(
        default=None,
        description="Minimum renewal date"
    ),
    end_date: date | None = Query(
        default=None,
        description="Maximum renewal date"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date cannot be later than end_date"
        )

    return generate_renewal_report(
        db,
        current_user,
        status,
        start_date,
        end_date
    )


# =========================================================
# COMPLIANCE REPORT
# GET /reports/compliance
# =========================================================

@router.get(
    "/reports/compliance",
    response_model=ComplianceReportResponse
)
def compliance_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return generate_compliance_report(
        db,
        current_user
    )


# =========================================================
# CONTRACT PDF EXPORT
# GET /reports/contracts/pdf
# =========================================================

@router.get("/reports/contracts/pdf")
def contract_report_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pdf_file = generate_pdf_report(
        db,
        current_user,
        "contract"
    )

    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                'attachment; filename="contract_report.pdf"'
            )
        }
    )


# =========================================================
# CONTRACT EXCEL EXPORT
# GET /reports/contracts/excel
# =========================================================

@router.get("/reports/contracts/excel")
def contract_report_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    excel_file = generate_excel_report(
        db,
        current_user,
        "contract"
    )

    return StreamingResponse(
        excel_file,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                'attachment; filename="contract_report.xlsx"'
            )
        }
    )


# =========================================================
# OBLIGATION PDF EXPORT
# GET /reports/obligations/pdf
# =========================================================

@router.get("/reports/obligations/pdf")
def obligation_report_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pdf_file = generate_pdf_report(
        db,
        current_user,
        "obligation"
    )

    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                'attachment; filename="obligation_report.pdf"'
            )
        }
    )


# =========================================================
# OBLIGATION EXCEL EXPORT
# GET /reports/obligations/excel
# =========================================================

@router.get("/reports/obligations/excel")
def obligation_report_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    excel_file = generate_excel_report(
        db,
        current_user,
        "obligation"
    )

    return StreamingResponse(
        excel_file,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                'attachment; filename="obligation_report.xlsx"'
            )
        }
    )


# =========================================================
# RENEWAL PDF EXPORT
# GET /reports/renewals/pdf
# =========================================================

@router.get("/reports/renewals/pdf")
def renewal_report_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pdf_file = generate_pdf_report(
        db,
        current_user,
        "renewal"
    )

    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                'attachment; filename="renewal_report.pdf"'
            )
        }
    )


# =========================================================
# RENEWAL EXCEL EXPORT
# GET /reports/renewals/excel
# =========================================================

@router.get("/reports/renewals/excel")
def renewal_report_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    excel_file = generate_excel_report(
        db,
        current_user,
        "renewal"
    )

    return StreamingResponse(
        excel_file,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                'attachment; filename="renewal_report.xlsx"'
            )
        }
    )


# =========================================================
# COMPLIANCE PDF EXPORT
# GET /reports/compliance/pdf
# =========================================================

@router.get("/reports/compliance/pdf")
def compliance_report_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pdf_file = generate_pdf_report(
        db,
        current_user,
        "compliance"
    )

    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                'attachment; filename="compliance_report.pdf"'
            )
        }
    )


# =========================================================
# COMPLIANCE EXCEL EXPORT
# GET /reports/compliance/excel
# =========================================================

@router.get("/reports/compliance/excel")
def compliance_report_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    excel_file = generate_excel_report(
        db,
        current_user,
        "compliance"
    )

    return StreamingResponse(
        excel_file,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                'attachment; filename="compliance_report.xlsx"'
            )
        }
    )