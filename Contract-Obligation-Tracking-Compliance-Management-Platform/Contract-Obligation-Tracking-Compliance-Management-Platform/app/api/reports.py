from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.utils.authorization import get_current_user
from app.services.report_service import (
    get_dashboard_summary,
    get_contract_summary,
    get_obligation_summary,
    get_renewal_summary,
    get_compliance_summary,
    get_risk_report,
    get_contract_report_rows,
    get_obligation_report_rows,
    get_renewal_report_rows,
    get_compliance_report_rows,
    generate_pdf,
    generate_excel,
)
from app.schemas.report import (
    DashboardSummary,
    ContractStatusStatistics,
    ObligationStatistics,
    RenewalStatistics,
    ComplianceStatistics,
    RiskSummary,
)


router = APIRouter(
    tags=["Reports & Analytics"]
)


@router.get(
    "/dashboard/summary",
    response_model=DashboardSummary,
)
def dashboard_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_dashboard_summary(db)


@router.get(
    "/reports/contracts/summary",
    response_model=ContractStatusStatistics,
)
def contract_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_contract_summary(db)


@router.get(
    "/reports/obligations/summary",
    response_model=ObligationStatistics,
)
def obligation_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_obligation_summary(db)


@router.get(
    "/reports/renewals/summary",
    response_model=RenewalStatistics,
)
def renewal_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_renewal_summary(db)


@router.get(
    "/reports/compliance/summary",
    response_model=ComplianceStatistics,
)
def compliance_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_compliance_summary(db)


@router.get(
    "/reports/risk",
    response_model=list[RiskSummary],
)
def risk_report(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_risk_report(db)


@router.get(
    "/reports/contracts/export/excel",
)
def export_contracts_excel(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = get_contract_report_rows(db)

    file = generate_excel(
        "Contracts",
        [
            "Contract Number",
            "Title",
            "Category",
            "Status",
            "Start Date",
            "End Date",
            "Assigned User",
        ],
        rows,
    )

    return StreamingResponse(
        file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=contracts.xlsx"
        },
    )


@router.get(
    "/reports/contracts/export/pdf",
)
def export_contracts_pdf(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = get_contract_report_rows(db)

    file = generate_pdf(
        "Contract Report",
        [
            "Contract Number",
            "Title",
            "Category",
            "Status",
            "Start Date",
            "End Date",
            "Assigned User",
        ],
        rows,
    )

    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=contracts.pdf"
        },
    )


@router.get(
    "/reports/obligations/export/excel",
)
def export_obligations_excel(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = get_obligation_report_rows(db)

    file = generate_excel(
        "Obligations",
        [
            "Contract ID",
            "Obligation Title",
            "Obligation Type",
            "Assigned User",
            "Due Date",
            "Status",
            "Completion Date",
        ],
        rows,
    )

    return StreamingResponse(
        file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=obligations.xlsx"
        },
    )


@router.get(
    "/reports/obligations/export/pdf",
)
def export_obligations_pdf(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = get_obligation_report_rows(db)

    file = generate_pdf(
        "Obligation Report",
        [
            "Contract ID",
            "Obligation Title",
            "Obligation Type",
            "Assigned User",
            "Due Date",
            "Status",
            "Completion Date",
        ],
        rows,
    )

    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=obligations.pdf"
        },
    )


@router.get(
    "/reports/renewals/export/excel",
)
def export_renewals_excel(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = get_renewal_report_rows(db)

    file = generate_excel(
        "Renewals",
        [
            "Contract ID",
            "Previous Expiry Date",
            "Renewal Date",
            "New Expiry Date",
            "Renewal Status",
            "Assigned User",
        ],
        rows,
    )

    return StreamingResponse(
        file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=renewals.xlsx"
        },
    )


@router.get(
    "/reports/renewals/export/pdf",
)
def export_renewals_pdf(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = get_renewal_report_rows(db)

    file = generate_pdf(
        "Renewal Report",
        [
            "Contract ID",
            "Previous Expiry Date",
            "Renewal Date",
            "New Expiry Date",
            "Renewal Status",
            "Assigned User",
        ],
        rows,
    )

    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=renewals.pdf"
        },
    )


@router.get(
    "/reports/compliance/export/excel",
)
def export_compliance_excel(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = get_compliance_report_rows(db)

    file = generate_excel(
        "Compliance",
        [
            "Contract Number",
            "Compliance Status",
            "Compliance Score",
            "Overdue Obligations",
            "Risk Level",
            "Evaluation Date",
        ],
        rows,
    )

    return StreamingResponse(
        file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=compliance.xlsx"
        },
    )


@router.get(
    "/reports/compliance/export/pdf",
)
def export_compliance_pdf(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = get_compliance_report_rows(db)

    file = generate_pdf(
        "Compliance Report",
        [
            "Contract Number",
            "Compliance Status",
            "Compliance Score",
            "Overdue Obligations",
            "Risk Level",
            "Evaluation Date",
        ],
        rows,
    )

    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=compliance.pdf"
        },
    )
