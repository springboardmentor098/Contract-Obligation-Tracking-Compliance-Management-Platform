from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.renewal import Renewal
from app.models.user import User

from app.routers.dependencies import get_current_user

from app.schemas.report import (
    ContractSummaryResponse,
    ContractStatusCount,
    ObligationSummaryResponse,
    ObligationStatusCount,
    RenewalSummaryResponse,
    RenewalItem,
    ComplianceSummaryResponse,
    DashboardResponse
)

from app.services.compliance_service import (
    calculate_contract_compliance
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports & Analytics"]
)


# ============================================================
# CONTRACT SUMMARY
# GET /reports/contracts
# ============================================================

@router.get(
    "/contracts",
    response_model=ContractSummaryResponse
)
def get_contract_summary(
    contract_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = db.query(Contract)

    if contract_status:
        query = query.filter(
            Contract.status == contract_status
        )

    total_contracts = query.count()

    active_contracts = query.filter(
        Contract.status == "Active"
    ).count()

    expired_contracts = query.filter(
        Contract.status == "Expired"
    ).count()

    pending_approval = query.filter(
        Contract.status == "Under Review"
    ).count()

    grouped = query.with_entities(
        Contract.status,
        func.count(Contract.id)
    ).group_by(
        Contract.status
    ).all()

    contracts_by_status = [
        ContractStatusCount(
            status=status_value,
            count=count
        )
        for status_value, count in grouped
    ]

    return ContractSummaryResponse(
        total_contracts=total_contracts,
        active_contracts=active_contracts,
        expired_contracts=expired_contracts,
        pending_approval=pending_approval,
        contracts_by_status=contracts_by_status
    )


# ============================================================
# OBLIGATION SUMMARY
# GET /reports/obligations
# ============================================================

@router.get(
    "/obligations",
    response_model=ObligationSummaryResponse
)
def get_obligation_summary(
    obligation_status: Optional[str] = None,
    contract_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = db.query(Obligation)

    if obligation_status:
        query = query.filter(
            Obligation.status == obligation_status
        )

    if contract_status:
        query = query.join(
            Contract,
            Obligation.contract_id == Contract.id
        ).filter(
            Contract.status == contract_status
        )

    total_obligations = query.count()

    pending_obligations = query.filter(
        Obligation.status == "Pending"
    ).count()

    completed_obligations = query.filter(
        Obligation.status == "Completed"
    ).count()

    today = date.today()

    overdue_obligations = query.filter(
        Obligation.due_date < today,
        Obligation.status != "Completed"
    ).count()

    grouped = query.with_entities(
        Obligation.status,
        func.count(Obligation.id)
    ).group_by(
        Obligation.status
    ).all()

    obligations_by_status = [
        ObligationStatusCount(
            status=status_value,
            count=count
        )
        for status_value, count in grouped
    ]

    return ObligationSummaryResponse(
        total_obligations=total_obligations,
        pending_obligations=pending_obligations,
        completed_obligations=completed_obligations,
        overdue_obligations=overdue_obligations,
        obligations_by_status=obligations_by_status
    )


# ============================================================
# RENEWAL SUMMARY
# GET /reports/renewals
# ============================================================

@router.get(
    "/renewals",
    response_model=RenewalSummaryResponse
)
def get_renewal_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    days: int = 90,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Days must be greater than 0"
        )

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after end date"
        )

    today = date.today()
    threshold_date = today + timedelta(days=days)

    # --------------------------------------------------------
    # Upcoming renewals
    # --------------------------------------------------------

    upcoming_query = db.query(
        Renewal,
        Contract.end_date
    ).join(
        Contract,
        Renewal.contract_id == Contract.id
    ).filter(
        Contract.end_date >= today,
        Contract.end_date <= threshold_date,
        Renewal.status.in_(
            ["Upcoming", "In Progress"]
        )
    )

    if start_date:
        upcoming_query = upcoming_query.filter(
            Renewal.renewal_date >= start_date
        )

    if end_date:
        upcoming_query = upcoming_query.filter(
            Renewal.renewal_date <= end_date
        )

    upcoming_results = upcoming_query.all()

    # --------------------------------------------------------
    # Expired contracts
    # --------------------------------------------------------

    expired_contracts = db.query(
        Contract.id
    ).filter(
        Contract.end_date < today
    ).count()

    # --------------------------------------------------------
    # Immediate attention
    # Contracts expiring within 30 days
    # --------------------------------------------------------

    attention_date = today + timedelta(days=30)

    immediate_attention = db.query(
        Contract.id
    ).filter(
        Contract.end_date >= today,
        Contract.end_date <= attention_date,
        Contract.status == "Active"
    ).count()

    renewals = [
        RenewalItem(
            renewal_id=renewal.id,
            contract_id=renewal.contract_id,
            renewal_date=renewal.renewal_date,
            contract_end_date=contract_end_date,
            status=renewal.status
        )
        for renewal, contract_end_date in upcoming_results
    ]

    return RenewalSummaryResponse(
        upcoming_renewals=len(upcoming_results),
        expired_contracts=expired_contracts,
        immediate_attention=immediate_attention,
        renewals=renewals
    )


# ============================================================
# COMPLIANCE SUMMARY
# GET /reports/compliance
# ============================================================

@router.get(
    "/compliance",
    response_model=ComplianceSummaryResponse
)
def get_compliance_summary(
    contract_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = db.query(Contract)

    if contract_status:
        query = query.filter(
            Contract.status == contract_status
        )

    contracts = query.all()

    total_contracts = len(contracts)

    compliant = 0
    partially_compliant = 0
    non_compliant = 0
    high_risk = 0

    total_completed = 0
    total_obligations = 0
    high_risk_obligations = 0

    for contract in contracts:

        result = calculate_contract_compliance(
            db,
            contract.id
        )

        total_obligations += result["total_obligations"]
        total_completed += result["completed_obligations"]

        if result["compliance_status"] == "Compliant":
            compliant += 1

        elif result["compliance_status"] == "Partially Compliant":
            partially_compliant += 1

        elif result["compliance_status"] == "Non-Compliant":
            non_compliant += 1

        if result["risk_level"] == "High":
            high_risk += 1

            # Existing compliance logic defines
            # High risk as 2 or more overdue obligations.
            high_risk_obligations += result[
                "overdue_obligations"
            ]

    if total_obligations > 0:
        overall_compliance_percentage = round(
            (total_completed / total_obligations) * 100,
            2
        )
    else:
        overall_compliance_percentage = 0.0

    return ComplianceSummaryResponse(
        total_contracts=total_contracts,
        compliant_contracts=compliant,
        partially_compliant_contracts=partially_compliant,
        non_compliant_contracts=non_compliant,
        high_risk_contracts=high_risk,
        high_risk_obligations=high_risk_obligations,
        overall_compliance_percentage=(
            overall_compliance_percentage
        )
    )


# ============================================================
# DASHBOARD SUMMARY
# GET /reports/dashboard
# ============================================================

@router.get(
    "/dashboard",
    response_model=DashboardResponse
)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    contracts = get_contract_summary(
        db=db,
        current_user=current_user
    )

    obligations = get_obligation_summary(
        db=db,
        current_user=current_user
    )

    renewals = get_renewal_summary(
        db=db,
        current_user=current_user
    )

    compliance = get_compliance_summary(
        db=db,
        current_user=current_user
    )

    return DashboardResponse(
        contracts=contracts,
        obligations=obligations,
        renewals=renewals,
        compliance=compliance
    )