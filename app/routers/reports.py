from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user

from app.models.user import User
from app.models.contracts import Contract
from app.models.obligations import Obligation
from app.models.renewal import Renewal
from fastapi.responses import StreamingResponse
from app.services.report_service import (
    get_contract_summary,
    get_obligation_summary,
    get_renewal_summary,
    generate_contract_pdf,
    generate_contract_excel
)
from app.services.compliance import (
    get_all_compliance,
    get_compliance_summary
)

from app.services.report_service import (
    get_contract_summary,
    get_obligation_summary,
    get_renewal_summary
)
from fastapi.responses import StreamingResponse

from app.services.report_service import generate_contract_pdf


# REPORTS ROUTER
router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


# CONTRACT REPORT SUMMARY
@router.get("/contracts/summary")
def get_contract_report_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_contract_summary(db)


# OBLIGATION REPORT SUMMARY
@router.get("/obligations/summary")
def get_obligation_report_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_obligation_summary(db)


# RENEWAL REPORT SUMMARY
@router.get("/renewals/summary")
def get_renewal_report_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_renewal_summary(db)


# COMPLIANCE REPORT SUMMARY
@router.get("/compliance/summary")
def get_compliance_report_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_compliance_summary(db)


# RISK REPORT
@router.get("/risk")
def get_risk_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    compliance_data = get_all_compliance(db)

    high_risk = []
    medium_risk = []
    low_risk = []

    for item in compliance_data:
        if item["risk_level"] == "High":
            high_risk.append(item)

        elif item["risk_level"] == "Medium":
            medium_risk.append(item)

        else:
            low_risk.append(item)

    return {
        "high_risk_contracts": high_risk,
        "medium_risk_contracts": medium_risk,
        "low_risk_contracts": low_risk
    }


# DASHBOARD ROUTER
dashboard_router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


# DASHBOARD SUMMARY
@dashboard_router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_contracts = db.query(Contract).count()

    active_contracts = db.query(Contract).filter(
        Contract.status == "Active"
    ).count()

    total_obligations = db.query(Obligation).count()

    completed_obligations = db.query(Obligation).filter(
        Obligation.status == "Completed"
    ).count()

    pending_obligations = db.query(Obligation).filter(
        Obligation.status == "Pending"
    ).count()

    overdue_obligations = db.query(Obligation).filter(
        Obligation.status == "Overdue"
    ).count()

    total_renewals = db.query(Renewal).count()

    upcoming_renewals = db.query(Renewal).filter(
        Renewal.status == "Upcoming"
    ).count()

    compliance = get_compliance_summary(db)

    return {
        "contracts": {
            "total": total_contracts,
            "active": active_contracts
        },
        "obligations": {
            "total": total_obligations,
            "completed": completed_obligations,
            "pending": pending_obligations,
            "overdue": overdue_obligations
        },
        "renewals": {
            "total": total_renewals,
            "upcoming": upcoming_renewals
        },
        "compliance": compliance
    }
# CONTRACT PDF EXPORT
@router.get("/contracts/export/pdf")
def export_contract_pdf(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pdf = generate_contract_pdf(db)

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=contract_report.pdf"
        }
    )
# CONTRACT EXCEL EXPORT
@router.get("/contracts/export/excel")
def export_contract_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    excel = generate_contract_excel(db)

    return StreamingResponse(
        excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=contract_report.xlsx"
        }
    )