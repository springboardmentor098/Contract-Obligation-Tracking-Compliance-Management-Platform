from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.core.auth import get_current_user

from backend.app.models.contract import Contract
from backend.app.models.obligation import Obligation
from backend.app.models.renewal import Renewal

from backend.app.services.compliance_service import (
    calculate_contract_compliance
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    # =====================
    # CONTRACT STATISTICS
    # =====================

    total_contracts = db.query(Contract).count()

    active_contracts = db.query(Contract).filter(
        Contract.status == "Active"
    ).count()

    draft_contracts = db.query(Contract).filter(
        Contract.status == "Draft"
    ).count()

    under_review_contracts = db.query(Contract).filter(
        Contract.status == "Under Review"
    ).count()

    expired_contracts = db.query(Contract).filter(
        Contract.status == "Expired"
    ).count()
    approved_contracts = db.query(Contract).filter(
    Contract.status == "Approved"
).count()
    terminated_contracts = db.query(Contract).filter(
    Contract.status == "Terminated"
).count()


    # =====================
    # OBLIGATION STATISTICS
    # =====================

    total_obligations = db.query(Obligation).count()

    pending_obligations = db.query(Obligation).filter(
        Obligation.status == "Pending"
    ).count()

    completed_obligations = db.query(Obligation).filter(
        Obligation.status == "Completed"
    ).count()

    overdue_obligations = db.query(Obligation).filter(
        Obligation.status == "Overdue"
    ).count()
    in_progress_obligations = db.query(Obligation).filter(
    Obligation.status == "In Progress"
).count()

    delayed_obligations = db.query(Obligation).filter(
    Obligation.status == "Delayed"
).count()


    # =====================
    # RENEWAL STATISTICS
    # =====================

    upcoming_renewals = db.query(Renewal).filter(
        Renewal.status == "Upcoming"
    ).count()
    in_progress_renewals = db.query(Renewal).filter(
    Renewal.status == "In Progress"
).count()

    renewed_renewals = db.query(Renewal).filter(
    Renewal.status == "Renewed"
).count()

    expired_renewals = db.query(Renewal).filter(
    Renewal.status == "Expired"
).count()

    cancelled_renewals = db.query(Renewal).filter(
    Renewal.status == "Cancelled"
).count()


    # =====================
    # COMPLIANCE STATISTICS
    # =====================

    contracts = db.query(Contract).all()

    compliant_contracts = 0
    pending_compliance = 0
    delayed_contracts = 0
    non_compliant_contracts = 0
    high_risk_contracts = 0

    for contract in contracts:

        result = calculate_contract_compliance(
            contract,
            db
        )

        if result["compliance_status"] == "Compliant":
            compliant_contracts += 1

        elif result["compliance_status"] == "Pending":
            pending_compliance += 1

        elif result["compliance_status"] == "Delayed":
            delayed_contracts += 1

        elif result["compliance_status"] == "Non-Compliant":
            non_compliant_contracts += 1

        if result["risk_level"] == "High":
            high_risk_contracts += 1


    # =====================
    # DASHBOARD RESPONSE
    # =====================

    return {
    "contracts": {
        "total": total_contracts,
        "active": active_contracts,
        "draft": draft_contracts,
        "under_review": under_review_contracts,
        "approved": approved_contracts,
        "expired": expired_contracts,
        "terminated": terminated_contracts
    },

    "obligations": {
        "total": total_obligations,
        "pending": pending_obligations,
        "in_progress": in_progress_obligations,
        "completed": completed_obligations,
        "delayed": delayed_obligations,
        "overdue": overdue_obligations
    },

    "renewals": {
        "upcoming": upcoming_renewals,
        "in_progress": in_progress_renewals,
        "renewed": renewed_renewals,
        "expired": expired_renewals,
        "cancelled": cancelled_renewals
    },

    "compliance": {
        "compliant": compliant_contracts,
        "pending": pending_compliance,
        "delayed": delayed_contracts,
        "non_compliant": non_compliant_contracts,
        "high_risk": high_risk_contracts
    }
}