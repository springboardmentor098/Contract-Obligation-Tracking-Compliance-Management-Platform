from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.core.auth import get_current_user
from backend.app.core.auth import require_role
from backend.app.core.roles import UserRole

from backend.app.services.report_service import (
    get_contract_summary,
    get_obligation_summary,
    get_renewal_summary,
    get_compliance_summary,
    get_risk_report,
    generate_contract_pdf,
   generate_contract_excel,
   generate_obligation_pdf,
   generate_obligation_excel,
   generate_renewal_pdf,
   generate_renewal_excel,
   generate_compliance_pdf,
   generate_compliance_excel,
   get_upcoming_expiry_contracts,
   get_department_performance,
   get_upcoming_renewals,
   get_overdue_obligations,
)



router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


# ============================================================
# CONTRACT ANALYTICS
# ============================================================

@router.get("/contracts/summary")
def contract_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_role(
            UserRole.ADMINISTRATOR,
            UserRole.LEGAL_MANAGER,
            UserRole.COMPLIANCE_OFFICER
        )
    )
):
    return get_contract_summary(db)


# ============================================================
# OBLIGATION ANALYTICS
# ============================================================

@router.get("/obligations/summary")
def obligation_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return get_obligation_summary(db)


# ============================================================
# RENEWAL ANALYTICS
# ============================================================

@router.get("/renewals/summary")
def renewal_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return get_renewal_summary(db)


# ============================================================
# COMPLIANCE ANALYTICS
# ============================================================

@router.get("/compliance/summary")
def compliance_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return get_compliance_summary(db)


# ============================================================
# RISK ANALYSIS
# ============================================================

@router.get("/risk")
def risk_report(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return get_risk_report(db)
# ============================================================
# EXPORT CONTRACT REPORT AS PDF
# ============================================================

@router.get("/contracts/export/pdf")
def export_contract_pdf(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    pdf_buffer = generate_contract_pdf(db)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=contract_report.pdf"
        }
    )
    # ============================================================
# EXPORT CONTRACT REPORT AS EXCEL
# ============================================================

@router.get("/contracts/export/excel")
def export_contract_excel(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    excel_buffer = generate_contract_excel(db)

    return StreamingResponse(
        excel_buffer,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
            "attachment; filename=contract_report.xlsx"
        }
    )
    # ============================================================
# EXPORT OBLIGATION REPORT AS PDF
# ============================================================

@router.get("/obligations/export/pdf")
def export_obligation_pdf(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    pdf_buffer = generate_obligation_pdf(db)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=obligation_report.pdf"
        }
    )
    # ============================================================
# EXPORT OBLIGATION REPORT AS EXCEL
# ============================================================

@router.get("/obligations/export/excel")
def export_obligation_excel(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    excel_buffer = generate_obligation_excel(db)

    return StreamingResponse(
        excel_buffer,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
            "attachment; filename=obligation_report.xlsx"
        }
    )
    # ============================================================
# EXPORT RENEWAL REPORT AS PDF
# ============================================================

@router.get("/renewals/export/pdf")
def export_renewal_pdf(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    pdf_buffer = generate_renewal_pdf(db)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=renewal_report.pdf"
        }
    )
    # ============================================================
# EXPORT RENEWAL REPORT AS EXCEL
# ============================================================

@router.get("/renewals/export/excel")
def export_renewal_excel(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    excel_buffer = generate_renewal_excel(db)

    return StreamingResponse(
        excel_buffer,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
            "attachment; filename=renewal_report.xlsx"
        }
    )
    # ============================================================
# EXPORT COMPLIANCE REPORT AS PDF
# ============================================================

@router.get("/compliance/export/pdf")
def export_compliance_pdf(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    pdf_buffer = generate_compliance_pdf(db)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=compliance_report.pdf"
        }
    )
    # ============================================================
# EXPORT COMPLIANCE REPORT AS EXCEL
# ============================================================

@router.get("/compliance/export/excel")
def export_compliance_excel(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    excel_buffer = generate_compliance_excel(db)

    return StreamingResponse(
        excel_buffer,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
            "attachment; filename=compliance_report.xlsx"
        }
    )
    # ============================================================
# UPCOMING EXPIRY CONTRACTS
# ============================================================

@router.get("/contracts/upcoming-expiry")
def upcoming_expiry_contracts(
    days: int = Query(
        default=30,
        ge=1,
        le=365,
        description="Number of days to check for upcoming contract expiry"
    ),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return get_upcoming_expiry_contracts(db, days)
# ============================================================
# DEPARTMENT PERFORMANCE
# ============================================================

@router.get("/departments/performance")
def department_performance(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return get_department_performance(db)
# ============================================================
# UPCOMING RENEWALS
# ============================================================

@router.get("/renewals/upcoming")
def upcoming_renewals(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return get_upcoming_renewals(db)
# ============================================================
# OVERDUE OBLIGATIONS
# ============================================================

@router.get("/obligations/overdue")
def overdue_obligations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return get_overdue_obligations(db)