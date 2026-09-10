from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.report import (
    DashboardSummary,
    ContractStats,
    ObligationStats,
    RenewalStats,
    ComplianceStats,
    RiskSummary,
    DepartmentPerformance,
)
from app.services.report_service import (
    get_dashboard_summary,
    get_contract_statistics,
    get_obligation_statistics,
    get_renewal_statistics,
    get_compliance_statistics,
    get_risk_summary,
    get_upcoming_renewals,
    get_overdue_obligations,
    get_department_performance,
)
from app.core.dependencies import get_current_user
from app.services.export_service import (
    generate_contract_pdf,
    generate_contract_excel,
    generate_obligation_pdf,
    generate_obligation_excel,
    generate_renewal_pdf,
    generate_renewal_excel,
    generate_compliance_pdf,
    generate_compliance_excel,
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports & Analytics"]
)

dashboard_router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

# ============================================================
# REPORT ACCESS CONTROL
# ============================================================

ALLOWED_REPORT_ROLES = {
    "ADMINISTRATOR",
    "LEGAL_MANAGER",
    "COMPLIANCE_OFFICER",
    "CONTRACT_MANAGER",
    "DEPARTMENT_HEAD",
}


def check_report_access(current_user: User):
    if current_user.role not in ALLOWED_REPORT_ROLES:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access reports."
        )


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

@dashboard_router.get(
    "/summary",
    response_model=DashboardSummary
)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_report_access(current_user)

    try:
        return get_dashboard_summary(db)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate dashboard summary: {str(exc)}"
        )


# ============================================================
# CONTRACT REPORT
# ============================================================

@router.get(
    "/contracts/summary",
    response_model=ContractStats
)
def contract_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_report_access(current_user)

    try:
        return get_contract_statistics(db)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate contract report: {str(exc)}"
        )


# ============================================================
# OBLIGATION REPORT
# ============================================================

@router.get(
    "/obligations/summary",
    response_model=ObligationStats
)
def obligation_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_report_access(current_user)

    try:
        return get_obligation_statistics(db)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate obligation report: {str(exc)}"
        )


# ============================================================
# RENEWAL REPORT
# ============================================================

@router.get(
    "/renewals/summary",
    response_model=RenewalStats
)
def renewal_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_report_access(current_user)

    try:
        return get_renewal_statistics(db)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate renewal report: {str(exc)}"
        )


# ============================================================
# COMPLIANCE REPORT
# ============================================================

@router.get(
    "/compliance/summary",
    response_model=ComplianceStats
)
def compliance_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_report_access(current_user)

    try:
        return get_compliance_statistics(db)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate compliance report: {str(exc)}"
        )


# ============================================================
# RISK REPORT
# ============================================================

@router.get(
    "/risk",
    response_model=RiskSummary
)
def risk_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_report_access(current_user)

    try:
        return get_risk_summary(db)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate risk report: {str(exc)}"
        )


# ============================================================
# UPCOMING RENEWALS
# ============================================================

@router.get(
    "/renewals/upcoming"
)
def upcoming_renewals_report(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_report_access(current_user)

    if days < 1 or days > 365:
        raise HTTPException(
            status_code=400,
            detail="Days must be between 1 and 365."
        )

    try:
        renewals = get_upcoming_renewals(
            db=db,
            days=days
        )

        return {
            "days": days,
            "count": len(renewals),
            "renewals": [
                {
                    "id": renewal.id,
                    "contract_id": renewal.contract_id,
                    "assigned_to": renewal.assigned_to,
                    "renewal_date": renewal.renewal_date,
                    "notice_days": renewal.notice_days,
                    "status": renewal.status,
                    "new_expiry_date": renewal.new_expiry_date,
                    "previous_expiry_date": renewal.previous_expiry_date,
                    "notes": renewal.notes,
                }
                for renewal in renewals
            ]
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate upcoming renewal report: {str(exc)}"
        )


# ============================================================
# OVERDUE OBLIGATIONS
# ============================================================

@router.get(
    "/obligations/overdue"
)
def overdue_obligations_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_report_access(current_user)

    try:
        obligations = get_overdue_obligations(db)

        return {
            "count": len(obligations),
            "obligations": [
                {
                    "id": obligation.id,
                    "contract_id": obligation.contract_id,
                    "assigned_to": obligation.assigned_to,
                    "title": obligation.title,
                    "obligation_type": obligation.obligation_type,
                    "due_date": obligation.due_date,
                    "status": obligation.status,
                    "priority": obligation.priority,
                }
                for obligation in obligations
            ]
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate overdue obligation report: {str(exc)}"
        )


# ============================================================
# DEPARTMENT PERFORMANCE
# ============================================================

@router.get(
    "/department-performance",
    response_model=list[DepartmentPerformance]
)
def department_performance_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_report_access(current_user)

    try:
        return get_department_performance(db)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate department performance report: {str(exc)}"
        )
    # ============================================================
# CONTRACT PDF EXPORT
# ============================================================

@router.get("/contracts/export/pdf")
def export_contracts_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_report_access(current_user)

    try:
        file = generate_contract_pdf(db)

        return StreamingResponse(
            file,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                    "attachment; filename=contract_report.pdf"
            }
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate contract PDF: {str(exc)}"
        )


# ============================================================
# CONTRACT EXCEL EXPORT
# ============================================================

@router.get("/contracts/export/excel")
def export_contracts_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_report_access(current_user)

    try:
        file = generate_contract_excel(db)

        return StreamingResponse(
            file,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition":
                    "attachment; filename=contract_report.xlsx"
            }
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate contract Excel: {str(exc)}"
        )


# ============================================================
# OBLIGATION PDF EXPORT
# ============================================================

@router.get("/obligations/export/pdf")
def export_obligations_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_report_access(current_user)

    try:
        file = generate_obligation_pdf(db)

        return StreamingResponse(
            file,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                    "attachment; filename=obligation_report.pdf"
            }
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate obligation PDF: {str(exc)}"
        )


# ============================================================
# OBLIGATION EXCEL EXPORT
# ============================================================

@router.get("/obligations/export/excel")
def export_obligations_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_report_access(current_user)

    try:
        file = generate_obligation_excel(db)

        return StreamingResponse(
            file,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition":
                    "attachment; filename=obligation_report.xlsx"
            }
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate obligation Excel: {str(exc)}"
        )


# ============================================================
# RENEWAL PDF EXPORT
# ============================================================

@router.get("/renewals/export/pdf")
def export_renewals_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_report_access(current_user)

    try:
        file = generate_renewal_pdf(db)

        return StreamingResponse(
            file,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                    "attachment; filename=renewal_report.pdf"
            }
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate renewal PDF: {str(exc)}"
        )


# ============================================================
# RENEWAL EXCEL EXPORT
# ============================================================

@router.get("/renewals/export/excel")
def export_renewals_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_report_access(current_user)

    try:
        file = generate_renewal_excel(db)

        return StreamingResponse(
            file,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition":
                    "attachment; filename=renewal_report.xlsx"
            }
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate renewal Excel: {str(exc)}"
        )


# ============================================================
# COMPLIANCE PDF EXPORT
# ============================================================

@router.get("/compliance/export/pdf")
def export_compliance_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_report_access(current_user)

    try:
        file = generate_compliance_pdf(db)

        return StreamingResponse(
            file,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                    "attachment; filename=compliance_report.pdf"
            }
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate compliance PDF: {str(exc)}"
        )


# ============================================================
# COMPLIANCE EXCEL EXPORT
# ============================================================

@router.get("/compliance/export/excel")
def export_compliance_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_report_access(current_user)

    try:
        file = generate_compliance_excel(db)

        return StreamingResponse(
            file,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            headers={
                "Content-Disposition":
                    "attachment; filename=compliance_report.xlsx"
            }
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate compliance Excel: {str(exc)}"
        )