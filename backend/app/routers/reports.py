from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.compliance import Compliance
from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.renewal import Renewal
from app.models.user import User
from app.schemas.report import (
    ContractStatusDistributionResponse,
    ContractSummaryResponse,
    DashboardResponse,
    ObligationStatusDistributionResponse,
    ObligationSummaryResponse,
    RenewalReportItem,
    RenewalSummaryResponse,
    StatusCount,
    ComplianceSummaryResponse,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports & Analytics"],
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def is_admin(current_user: User) -> bool:
    """
    Administrators can see all reporting data.
    """
    return current_user.role.lower() in {
        "admin",
        "administrator",
    }


def apply_contract_access_filter(
    query,
    current_user: User,
):
    """
    Restrict non-admin users to contracts they created
    or contracts assigned to them.
    """
    if not is_admin(current_user):
        query = query.where(
            (Contract.created_by == current_user.id)
            | (Contract.assigned_to == current_user.id)
        )

    return query


def apply_obligation_access_filter(
    query,
    current_user: User,
):
    """
    Restrict non-admin users to obligations belonging to
    contracts they can access or obligations assigned to them.
    """
    if not is_admin(current_user):
        query = query.where(
            (Contract.created_by == current_user.id)
            | (Contract.assigned_to == current_user.id)
            | (Obligation.assigned_to == current_user.id)
        )

    return query


def apply_renewal_access_filter(
    query,
    current_user: User,
):
    """
    Restrict non-admin users to renewals belonging to
    accessible contracts or assigned to them.
    """
    if not is_admin(current_user):
        query = query.where(
            (Contract.created_by == current_user.id)
            | (Contract.assigned_to == current_user.id)
            | (Renewal.assigned_to == current_user.id)
        )

    return query


# ============================================================
# 1. CONTRACT SUMMARY
# ============================================================

@router.get(
    "/contracts/summary",
    response_model=ContractSummaryResponse,
)
def get_contract_summary(
    contract_status: str | None = Query(
        default=None,
        description="Optional contract status filter",
    ),
    date_from: date | None = Query(
        default=None,
        description="Optional contract start date from",
    ),
    date_to: date | None = Query(
        default=None,
        description="Optional contract start date to",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return contract summary statistics.
    """

    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_from cannot be greater than date_to",
        )

    today = date.today()

    query = select(Contract)

    query = apply_contract_access_filter(
        query,
        current_user,
    )

    if contract_status:
        query = query.where(
            Contract.status == contract_status.strip()
        )

    if date_from:
        query = query.where(
            Contract.start_date >= date_from
        )

    if date_to:
        query = query.where(
            Contract.start_date <= date_to
        )

    contracts = db.execute(query).scalars().all()

    total_contracts = len(contracts)

    active_contracts = sum(
        1
        for contract in contracts
        if contract.status == "Active"
    )

    expired_contracts = sum(
        1
        for contract in contracts
        if contract.end_date is not None
        and contract.end_date < today
    )

    pending_approval = sum(
        1
        for contract in contracts
        if contract.status == "Under Review"
    )

    return ContractSummaryResponse(
        total_contracts=total_contracts,
        active_contracts=active_contracts,
        expired_contracts=expired_contracts,
        pending_approval=pending_approval,
    )


# ============================================================
# 2. CONTRACT STATUS DISTRIBUTION
# ============================================================

@router.get(
    "/contracts/status-distribution",
    response_model=ContractStatusDistributionResponse,
)
def get_contract_status_distribution(
    contract_status: str | None = Query(
        default=None,
        description="Optional contract status filter",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return contracts grouped by status.
    """

    query = (
        select(
            Contract.status,
            func.count(Contract.id),
        )
        .group_by(Contract.status)
        .order_by(Contract.status)
    )

    query = apply_contract_access_filter(
        query,
        current_user,
    )

    if contract_status:
        query = query.where(
            Contract.status == contract_status.strip()
        )

    rows = db.execute(query).all()

    return ContractStatusDistributionResponse(
        data=[
            StatusCount(
                status=row[0],
                count=row[1],
            )
            for row in rows
        ]
    )


# ============================================================
# 3. OBLIGATION SUMMARY
# ============================================================

@router.get(
    "/obligations/summary",
    response_model=ObligationSummaryResponse,
)
def get_obligation_summary(
    obligation_status: str | None = Query(
        default=None,
        description="Optional obligation status filter",
    ),
    contract_status: str | None = Query(
        default=None,
        description="Optional contract status filter",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return obligation summary statistics.
    """

    today = date.today()

    query = (
        select(Obligation)
        .join(
            Contract,
            Obligation.contract_id == Contract.id,
        )
    )

    query = apply_obligation_access_filter(
        query,
        current_user,
    )

    if obligation_status:
        query = query.where(
            Obligation.status == obligation_status.strip()
        )

    if contract_status:
        query = query.where(
            Contract.status == contract_status.strip()
        )

    obligations = db.execute(query).scalars().all()

    total_obligations = len(obligations)

    completed_obligations = sum(
        1
        for obligation in obligations
        if obligation.status == "Completed"
    )

    pending_obligations = sum(
        1
        for obligation in obligations
        if obligation.status == "Pending"
    )

    overdue_obligations = sum(
        1
        for obligation in obligations
        if (
            obligation.due_date is not None
            and obligation.due_date < today
            and obligation.status != "Completed"
        )
    )

    return ObligationSummaryResponse(
        total_obligations=total_obligations,
        pending_obligations=pending_obligations,
        completed_obligations=completed_obligations,
        overdue_obligations=overdue_obligations,
    )


# ============================================================
# 4. OBLIGATION STATUS DISTRIBUTION
# ============================================================

@router.get(
    "/obligations/status-distribution",
    response_model=ObligationStatusDistributionResponse,
)
def get_obligation_status_distribution(
    obligation_status: str | None = Query(
        default=None,
        description="Optional obligation status filter",
    ),
    contract_status: str | None = Query(
        default=None,
        description="Optional contract status filter",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return obligations grouped by status.
    """

    query = (
        select(
            Obligation.status,
            func.count(Obligation.id),
        )
        .join(
            Contract,
            Obligation.contract_id == Contract.id,
        )
        .group_by(Obligation.status)
        .order_by(Obligation.status)
    )

    query = apply_obligation_access_filter(
        query,
        current_user,
    )

    if obligation_status:
        query = query.where(
            Obligation.status == obligation_status.strip()
        )

    if contract_status:
        query = query.where(
            Contract.status == contract_status.strip()
        )

    rows = db.execute(query).all()

    return ObligationStatusDistributionResponse(
        data=[
            StatusCount(
                status=row[0] or "Unknown",
                count=row[1],
            )
            for row in rows
        ]
    )


# ============================================================
# 5. UPCOMING RENEWALS
# ============================================================

@router.get(
    "/renewals/upcoming",
    response_model=list[RenewalReportItem],
)
def get_upcoming_renewals(
    days: int = Query(
        default=30,
        ge=1,
        le=365,
        description="Number of upcoming days to check",
    ),
    contract_status: str | None = Query(
        default=None,
        description="Optional contract status filter",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return renewals occurring within the selected number of days.
    """

    today = date.today()
    expiry_limit = today + timedelta(days=days)

    query = (
        select(Renewal)
        .join(
            Contract,
            Renewal.contract_id == Contract.id,
        )
        .where(
            Renewal.renewal_date.is_not(None),
            Renewal.renewal_date >= today,
            Renewal.renewal_date <= expiry_limit,
            Renewal.status.in_(
                ["Upcoming", "In Progress"]
            ),
        )
        .order_by(Renewal.renewal_date.asc())
    )

    query = apply_renewal_access_filter(
        query,
        current_user,
    )

    if contract_status:
        query = query.where(
            Contract.status == contract_status.strip()
        )

    return db.execute(query).scalars().unique().all()


# ============================================================
# 6. EXPIRED CONTRACTS / RENEWALS
# ============================================================

@router.get(
    "/renewals/expired",
    response_model=list[RenewalReportItem],
)
def get_expired_renewals(
    contract_status: str | None = Query(
        default=None,
        description="Optional contract status filter",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return renewal records whose related contract has expired.
    """

    today = date.today()

    query = (
        select(Renewal)
        .join(
            Contract,
            Renewal.contract_id == Contract.id,
        )
        .where(
            Contract.end_date.is_not(None),
            Contract.end_date < today,
        )
        .order_by(Contract.end_date.asc())
    )

    query = apply_renewal_access_filter(
        query,
        current_user,
    )

    if contract_status:
        query = query.where(
            Contract.status == contract_status.strip()
        )

    return db.execute(query).scalars().unique().all()


# ============================================================
# 7. CONTRACTS REQUIRING IMMEDIATE ATTENTION
# ============================================================

@router.get(
    "/renewals/attention",
    response_model=list[RenewalReportItem],
)
def get_renewals_requiring_attention(
    days: int = Query(
        default=30,
        ge=1,
        le=365,
        description="Renewals within this many days require attention",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return renewals requiring immediate attention.

    A renewal requires attention when:
    - Its contract has already expired, OR
    - Its renewal date is within the selected number of days.
    """

    today = date.today()
    attention_limit = today + timedelta(days=days)

    query = (
        select(Renewal)
        .join(
            Contract,
            Renewal.contract_id == Contract.id,
        )
        .where(
            (
                Contract.end_date.is_not(None)
                & (Contract.end_date < today)
            )
            |
            (
                Renewal.renewal_date.is_not(None)
                & (Renewal.renewal_date >= today)
                & (Renewal.renewal_date <= attention_limit)
                & Renewal.status.in_(
                    ["Upcoming", "In Progress"]
                )
            )
        )
        .order_by(
            Renewal.renewal_date.asc()
        )
    )

    query = apply_renewal_access_filter(
        query,
        current_user,
    )

    return db.execute(query).scalars().unique().all()


# ============================================================
# 8. RENEWALS WITHIN DATE RANGE
# ============================================================

@router.get(
    "/renewals/date-range",
    response_model=list[RenewalReportItem],
)
def get_renewals_by_date_range(
    date_from: date = Query(
        ...,
        description="Start date",
    ),
    date_to: date = Query(
        ...,
        description="End date",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return renewals within a selected date range.
    """

    if date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_from cannot be greater than date_to",
        )

    query = (
        select(Renewal)
        .join(
            Contract,
            Renewal.contract_id == Contract.id,
        )
        .where(
            Renewal.renewal_date.is_not(None),
            Renewal.renewal_date >= date_from,
            Renewal.renewal_date <= date_to,
        )
        .order_by(Renewal.renewal_date.asc())
    )

    query = apply_renewal_access_filter(
        query,
        current_user,
    )

    return db.execute(query).scalars().unique().all()


# ============================================================
# 9. COMPLIANCE SUMMARY
# ============================================================

@router.get(
    "/compliance/summary",
    response_model=ComplianceSummaryResponse,
)
def get_compliance_summary(
    contract_status: str | None = Query(
        default=None,
        description="Optional contract status filter",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return overall compliance statistics.

    Only the latest compliance evaluation for each contract
    is considered.
    """

    # Latest evaluation time for every contract.
    latest_compliance = (
        select(
            Compliance.contract_id,
            func.max(Compliance.evaluated_at).label(
                "latest_evaluated_at"
            ),
        )
        .group_by(Compliance.contract_id)
        .subquery()
    )

    query = (
        select(Compliance)
        .join(
            latest_compliance,
            (Compliance.contract_id == latest_compliance.c.contract_id)
            & (
                Compliance.evaluated_at
                == latest_compliance.c.latest_evaluated_at
            ),
        )
        .join(
            Contract,
            Compliance.contract_id == Contract.id,
        )
    )

    if not is_admin(current_user):
        query = query.where(
            (Contract.created_by == current_user.id)
            | (Contract.assigned_to == current_user.id)
        )

    if contract_status:
        query = query.where(
            Contract.status == contract_status.strip()
        )

    records = db.execute(query).scalars().all()

    total_contracts = len(records)

    compliant_contracts = sum(
        1
        for record in records
        if record.compliance_status == "Compliant"
    )

    non_compliant_contracts = sum(
        1
        for record in records
        if record.compliance_status == "Non-Compliant"
    )

    high_risk_contracts = sum(
        1
        for record in records
        if record.risk_level == "High"
    )

    # High-risk obligations are represented by
    # obligations with High priority.
    high_risk_obligations_query = (
        select(func.count(Obligation.id))
        .join(
            Contract,
            Obligation.contract_id == Contract.id,
        )
        .where(
            Obligation.priority == "High"
        )
    )

    high_risk_obligations_query = apply_obligation_access_filter(
        high_risk_obligations_query,
        current_user,
    )

    if contract_status:
        high_risk_obligations_query = high_risk_obligations_query.where(
            Contract.status == contract_status.strip()
        )

    high_risk_obligations = (
        db.execute(high_risk_obligations_query).scalar() or 0
    )

    average_compliance_score = (
        round(
            sum(
                record.compliance_score
                for record in records
            )
            / total_contracts,
            2,
        )
        if total_contracts
        else 0.0
    )

    return ComplianceSummaryResponse(
        total_contracts=total_contracts,
        compliant_contracts=compliant_contracts,
        non_compliant_contracts=non_compliant_contracts,
        high_risk_contracts=high_risk_contracts,
        high_risk_obligations=high_risk_obligations,
        average_compliance_score=average_compliance_score,
    )


# ============================================================
# 10. COMPLETE DASHBOARD DATA
# ============================================================

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
)
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return all data required by the dashboard.
    """

    # --------------------------------------------------------
    # CONTRACT SUMMARY
    # --------------------------------------------------------

    contract_query = select(Contract)

    contract_query = apply_contract_access_filter(
        contract_query,
        current_user,
    )

    contracts = db.execute(
        contract_query
    ).scalars().all()

    today = date.today()

    contract_summary = ContractSummaryResponse(
        total_contracts=len(contracts),
        active_contracts=sum(
            1
            for contract in contracts
            if contract.status == "Active"
        ),
        expired_contracts=sum(
            1
            for contract in contracts
            if contract.end_date is not None
            and contract.end_date < today
        ),
        pending_approval=sum(
            1
            for contract in contracts
            if contract.status == "Under Review"
        ),
    )

    # --------------------------------------------------------
    # CONTRACT STATUS DISTRIBUTION
    # --------------------------------------------------------

    contract_distribution_query = (
        select(
            Contract.status,
            func.count(Contract.id),
        )
        .group_by(Contract.status)
        .order_by(Contract.status)
    )

    contract_distribution_query = apply_contract_access_filter(
        contract_distribution_query,
        current_user,
    )

    contract_rows = db.execute(
        contract_distribution_query
    ).all()

    contract_distribution = [
        StatusCount(
            status=row[0],
            count=row[1],
        )
        for row in contract_rows
    ]

    # --------------------------------------------------------
    # OBLIGATION SUMMARY
    # --------------------------------------------------------

    obligation_query = (
        select(Obligation)
        .join(
            Contract,
            Obligation.contract_id == Contract.id,
        )
    )

    obligation_query = apply_obligation_access_filter(
        obligation_query,
        current_user,
    )

    obligations = db.execute(
        obligation_query
    ).scalars().all()

    obligation_summary = ObligationSummaryResponse(
        total_obligations=len(obligations),
        pending_obligations=sum(
            1
            for obligation in obligations
            if obligation.status == "Pending"
        ),
        completed_obligations=sum(
            1
            for obligation in obligations
            if obligation.status == "Completed"
        ),
        overdue_obligations=sum(
            1
            for obligation in obligations
            if obligation.due_date is not None
            and obligation.due_date < today
            and obligation.status != "Completed"
        ),
    )

    # --------------------------------------------------------
    # OBLIGATION STATUS DISTRIBUTION
    # --------------------------------------------------------

    obligation_distribution_query = (
        select(
            Obligation.status,
            func.count(Obligation.id),
        )
        .join(
            Contract,
            Obligation.contract_id == Contract.id,
        )
        .group_by(Obligation.status)
        .order_by(Obligation.status)
    )

    obligation_distribution_query = apply_obligation_access_filter(
        obligation_distribution_query,
        current_user,
    )

    obligation_rows = db.execute(
        obligation_distribution_query
    ).all()

    obligation_distribution = [
        StatusCount(
            status=row[0] or "Unknown",
            count=row[1],
        )
        for row in obligation_rows
    ]

    # --------------------------------------------------------
    # UPCOMING RENEWALS
    # --------------------------------------------------------

    renewal_limit = today + timedelta(days=30)

    upcoming_query = (
        select(Renewal)
        .join(
            Contract,
            Renewal.contract_id == Contract.id,
        )
        .where(
            Renewal.renewal_date.is_not(None),
            Renewal.renewal_date >= today,
            Renewal.renewal_date <= renewal_limit,
            Renewal.status.in_(
                ["Upcoming", "In Progress"]
            ),
        )
        .order_by(Renewal.renewal_date.asc())
    )

    upcoming_query = apply_renewal_access_filter(
        upcoming_query,
        current_user,
    )

    upcoming_renewals = db.execute(
        upcoming_query
    ).scalars().unique().all()

    # --------------------------------------------------------
    # EXPIRED CONTRACT COUNT
    # --------------------------------------------------------

    expired_contracts = sum(
        1
        for contract in contracts
        if contract.end_date is not None
        and contract.end_date < today
    )

    # --------------------------------------------------------
    # IMMEDIATE ATTENTION COUNT
    # --------------------------------------------------------

    attention_query = (
        select(func.count(func.distinct(Renewal.id)))
        .join(
            Contract,
            Renewal.contract_id == Contract.id,
        )
        .where(
            (
                Contract.end_date.is_not(None)
                & (Contract.end_date < today)
            )
            |
            (
                Renewal.renewal_date.is_not(None)
                & (Renewal.renewal_date >= today)
                & (Renewal.renewal_date <= renewal_limit)
                & Renewal.status.in_(
                    ["Upcoming", "In Progress"]
                )
            )
        )
    )

    attention_query = apply_renewal_access_filter(
        attention_query,
        current_user,
    )

    contracts_requiring_attention = (
        db.execute(attention_query).scalar() or 0
    )

    renewal_summary = RenewalSummaryResponse(
        upcoming_renewals=upcoming_renewals,
        expired_contracts=expired_contracts,
        contracts_requiring_attention=contracts_requiring_attention,
    )

    # --------------------------------------------------------
    # COMPLIANCE SUMMARY
    # --------------------------------------------------------

    latest_compliance = (
        select(
            Compliance.contract_id,
            func.max(Compliance.evaluated_at).label(
                "latest_evaluated_at"
            ),
        )
        .group_by(Compliance.contract_id)
        .subquery()
    )

    compliance_query = (
        select(Compliance)
        .join(
            latest_compliance,
            (Compliance.contract_id == latest_compliance.c.contract_id)
            & (
                Compliance.evaluated_at
                == latest_compliance.c.latest_evaluated_at
            ),
        )
        .join(
            Contract,
            Compliance.contract_id == Contract.id,
        )
    )

    if not is_admin(current_user):
        compliance_query = compliance_query.where(
            (Contract.created_by == current_user.id)
            | (Contract.assigned_to == current_user.id)
        )

    compliance_records = db.execute(
        compliance_query
    ).scalars().all()

    total_compliance = len(compliance_records)

    compliant_contracts = sum(
        1
        for record in compliance_records
        if record.compliance_status == "Compliant"
    )

    non_compliant_contracts = sum(
        1
        for record in compliance_records
        if record.compliance_status == "Non-Compliant"
    )

    high_risk_contracts = sum(
        1
        for record in compliance_records
        if record.risk_level == "High"
    )

    # High-risk obligations are represented by
    # obligations with High priority.
    high_risk_obligations_query = (
        select(func.count(Obligation.id))
        .join(
            Contract,
            Obligation.contract_id == Contract.id,
        )
        .where(
            Obligation.priority == "High"
        )
    )

    high_risk_obligations_query = apply_obligation_access_filter(
        high_risk_obligations_query,
        current_user,
    )

    high_risk_obligations = (
        db.execute(high_risk_obligations_query).scalar() or 0
    )

    average_score = (
        round(
            sum(
                record.compliance_score
                for record in compliance_records
            )
            / total_compliance,
            2,
        )
        if total_compliance
        else 0.0
    )

    compliance_summary = ComplianceSummaryResponse(
        total_contracts=total_compliance,
        compliant_contracts=compliant_contracts,
        non_compliant_contracts=non_compliant_contracts,
        high_risk_contracts=high_risk_contracts,
        high_risk_obligations=high_risk_obligations,
        average_compliance_score=average_score,
    )

    # --------------------------------------------------------
    # FINAL DASHBOARD RESPONSE
    # --------------------------------------------------------

    return DashboardResponse(
        contracts=contract_summary,
        contract_status_distribution=contract_distribution,
        obligations=obligation_summary,
        obligation_status_distribution=obligation_distribution,
        renewals=renewal_summary,
        compliance=compliance_summary,
    )