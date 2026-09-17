from datetime import date

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.core.dependencies import require_role

from app.schemas.report import (
    DashboardSummary,
    ContractStats,
    ObligationStats,
    RenewalStats,
    ComplianceStats,
    RiskSummary
)

from app.services.report_service import (
    get_dashboard_summary,
    get_contract_stats,
    get_obligation_stats,
    get_renewal_stats,
    get_compliance_stats,
    get_risk_summary,
    get_contract_report_data,
    get_obligation_report_data,
    get_renewal_report_data,
    get_compliance_report_data,
    generate_pdf_report,
    generate_excel_report
)

router = APIRouter(
    tags=["Reports"]
)

REPORT_ROLES = [
    "Administrator",
    "Contract Manager",
    "Compliance Officer"
]


@router.get(
    "/dashboard/summary",
    response_model=DashboardSummary
)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(REPORT_ROLES)
    )
):
    return get_dashboard_summary(db)


@router.get(
    "/reports/contracts/summary",
    response_model=ContractStats
)
def contract_summary(
    start_date: date | None = None,
    end_date: date | None = None,
    status: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(REPORT_ROLES)
    )
):
    return get_contract_stats(
        db,
        start_date=start_date,
        end_date=end_date,
        status=status,
        category=category
    )


@router.get(
    "/reports/obligations/summary",
    response_model=ObligationStats
)
def obligation_summary(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(REPORT_ROLES)
    )
):
    return get_obligation_stats(
        db,
        start_date=start_date,
        end_date=end_date
    )


@router.get(
    "/reports/renewals/summary",
    response_model=RenewalStats
)
def renewal_summary(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(REPORT_ROLES)
    )
):
    return get_renewal_stats(
        db,
        start_date=start_date,
        end_date=end_date
    )


@router.get(
    "/reports/compliance/summary",
    response_model=ComplianceStats
)
def compliance_summary(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(REPORT_ROLES)
    )
):
    return get_compliance_stats(
        db,
        start_date=start_date,
        end_date=end_date
    )


@router.get(
    "/reports/risk",
    response_model=RiskSummary
)
def risk_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(REPORT_ROLES)
    )
):
    return get_risk_summary(db)


@router.get("/reports/contracts/export/pdf")
def export_contracts_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(REPORT_ROLES)
    )
):
    rows = get_contract_report_data(db)

    buffer = generate_pdf_report(
        "Contract Report",
        rows
    )

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=contract_report.pdf"
        }
    )


@router.get("/reports/contracts/export/excel")
def export_contracts_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(REPORT_ROLES)
    )
):
    rows = get_contract_report_data(db)

    buffer = generate_excel_report(
        "Contract Report",
        rows
    )

    return StreamingResponse(
        buffer,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=contract_report.xlsx"
        }
    )


@router.get("/reports/obligations/export/pdf")
def export_obligations_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(REPORT_ROLES)
    )
):
    rows = get_obligation_report_data(db)

    buffer = generate_pdf_report(
        "Obligation Report",
        rows
    )

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=obligation_report.pdf"
        }
    )


@router.get("/reports/obligations/export/excel")
def export_obligations_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(REPORT_ROLES)
    )
):
    rows = get_obligation_report_data(db)

    buffer = generate_excel_report(
        "Obligation Report",
        rows
    )

    return StreamingResponse(
        buffer,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=obligation_report.xlsx"
        }
    )


@router.get("/reports/renewals/export/pdf")
def export_renewals_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(REPORT_ROLES)
    )
):
    rows = get_renewal_report_data(db)

    buffer = generate_pdf_report(
        "Renewal Report",
        rows
    )

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=renewal_report.pdf"
        }
    )


@router.get("/reports/renewals/export/excel")
def export_renewals_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(REPORT_ROLES)
    )
):
    rows = get_renewal_report_data(db)

    buffer = generate_excel_report(
        "Renewal Report",
        rows
    )

    return StreamingResponse(
        buffer,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=renewal_report.xlsx"
        }
    )


@router.get("/reports/compliance/export/pdf")
def export_compliance_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(REPORT_ROLES)
    )
):
    rows = get_compliance_report_data(db)

    buffer = generate_pdf_report(
        "Compliance Report",
        rows
    )

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=compliance_report.pdf"
        }
    )


@router.get("/reports/compliance/export/excel")
def export_compliance_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role(REPORT_ROLES)
    )
):
    rows = get_compliance_report_data(db)

    buffer = generate_excel_report(
        "Compliance Report",
        rows
    )

    return StreamingResponse(
        buffer,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=compliance_report.xlsx"
        }
    )
