from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.core.security import get_current_user

from app.schemas.reports import (
    ContractReportResponse,
    ObligationReportResponse,
    RenewalReportResponse,
    ComplianceReportResponse,
    AuditReportResponse,
)

from app.services.report_service import (
    generate_contract_report,
    generate_obligation_report,
    generate_renewal_report,
    generate_compliance_report,
    generate_audit_report,
    contract_pdf,
    obligation_pdf,
    renewal_pdf,
    compliance_pdf,
    audit_pdf,
    contract_excel,
    obligation_excel,
    renewal_excel,
    compliance_excel,
    audit_excel,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


# ============================================================
# REPORT APIs
# ============================================================

@router.get(
    "/contracts",
    response_model=ContractReportResponse,
)
def contract_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return generate_contract_report(db)


@router.get(
    "/obligations",
    response_model=ObligationReportResponse,
)
def obligation_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return generate_obligation_report(db)


@router.get(
    "/renewals",
    response_model=RenewalReportResponse,
)
def renewal_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return generate_renewal_report(db)


@router.get(
    "/compliance",
    response_model=ComplianceReportResponse,
)
def compliance_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return generate_compliance_report(db)


@router.get(
    "/audit",
    response_model=AuditReportResponse,
)
def audit_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return generate_audit_report(db)


# ============================================================
# CONTRACT EXPORT
# ============================================================

@router.get("/contracts/export/pdf")
def export_contract_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file = contract_pdf(db)

    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=contract_report.pdf"
        },
    )


@router.get("/contracts/export/excel")
def export_contract_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file = contract_excel(db)

    return StreamingResponse(
        file,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=contract_report.xlsx"
        },
    )


# ============================================================
# OBLIGATION EXPORT
# ============================================================

@router.get("/obligations/export/pdf")
def export_obligation_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file = obligation_pdf(db)

    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=obligation_report.pdf"
        },
    )


@router.get("/obligations/export/excel")
def export_obligation_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file = obligation_excel(db)

    return StreamingResponse(
        file,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=obligation_report.xlsx"
        },
    )


# ============================================================
# RENEWAL EXPORT
# ============================================================

@router.get("/renewals/export/pdf")
def export_renewal_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file = renewal_pdf(db)

    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=renewal_report.pdf"
        },
    )


@router.get("/renewals/export/excel")
def export_renewal_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file = renewal_excel(db)

    return StreamingResponse(
        file,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=renewal_report.xlsx"
        },
    )


# ============================================================
# COMPLIANCE EXPORT
# ============================================================

@router.get("/compliance/export/pdf")
def export_compliance_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file = compliance_pdf(db)

    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=compliance_report.pdf"
        },
    )


@router.get("/compliance/export/excel")
def export_compliance_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file = compliance_excel(db)

    return StreamingResponse(
        file,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=compliance_report.xlsx"
        },
    )


# ============================================================
# AUDIT EXPORT
# ============================================================

@router.get("/audit/export/pdf")
def export_audit_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file = audit_pdf(db)

    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=audit_report.pdf"
        },
    )


@router.get("/audit/export/excel")
def export_audit_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file = audit_excel(db)

    return StreamingResponse(
        file,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=audit_report.xlsx"
        },
    )