from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.renewal import Renewal

from app.services.compliance_service import (
    calculate_contract_compliance,
)


# ============================================================
# CONTRACT REPORT
# ============================================================

def get_contract_summary(
    db: Session,
    status: Optional[str] = None,
):
    query = db.query(Contract)

    if status:
        query = query.filter(
            Contract.status == status
        )

    contracts = (
        query
        .order_by(Contract.id)
        .all()
    )

    total = len(contracts)

    active = sum(
        1
        for contract in contracts
        if contract.status == "Active"
    )

    expired = sum(
        1
        for contract in contracts
        if contract.status == "Expired"
    )

    pending_approval = sum(
        1
        for contract in contracts
        if contract.status in {
            "Under Review",
            "Pending Approval",
        }
    )

    grouped = {}

    for contract in contracts:
        contract_status = (
            contract.status or "Unknown"
        )

        grouped[contract_status] = (
            grouped.get(contract_status, 0) + 1
        )

    contract_records = []

    for contract in contracts:
        contract_records.append(
            {
                "id": contract.id,
                "contract_number": contract.contract_number,
                "title": contract.title,
                "category": contract.category,
                "start_date": (
                    contract.start_date.isoformat()
                    if contract.start_date
                    else ""
                ),
                "end_date": (
                    contract.end_date.isoformat()
                    if contract.end_date
                    else ""
                ),
                "status": contract.status,
                "created_by": contract.created_by,
                "assigned_to": contract.assigned_to,
            }
        )

    return {
        "total_contracts": total,
        "active_contracts": active,
        "expired_contracts": expired,
        "pending_approval_contracts": pending_approval,
        "contracts_by_status": grouped,
        "contract_records": contract_records,
    }


# ============================================================
# OBLIGATION REPORT
# ============================================================

def get_obligation_summary(
    db: Session,
    status: Optional[str] = None,
):
    query = db.query(Obligation)

    if status:
        query = query.filter(
            Obligation.status == status
        )

    obligations = (
        query
        .order_by(Obligation.id)
        .all()
    )

    today = date.today()

    total = len(obligations)

    pending = 0
    completed = 0
    overdue = 0

    grouped = {}

    obligation_records = []

    for obligation in obligations:

        obligation_status = (
            obligation.status or "Unknown"
        )

        grouped[obligation_status] = (
            grouped.get(obligation_status, 0) + 1
        )

        if obligation_status == "Completed":

            completed += 1

        elif obligation_status == "Overdue":

            overdue += 1

        elif (
            obligation_status == "Pending"
            and obligation.due_date
            and obligation.due_date < today
        ):

            overdue += 1

        elif obligation_status == "Pending":

            pending += 1

        contract = (
            db.query(Contract)
            .filter(
                Contract.id
                == obligation.contract_id
            )
            .first()
        )

        obligation_records.append(
            {
                "id": obligation.id,
                "contract_id": obligation.contract_id,
                "contract_number": (
                    contract.contract_number
                    if contract
                    else None
                ),
                "contract_title": (
                    contract.title
                    if contract
                    else None
                ),
                "title": obligation.title,
                "description": obligation.description,
                "obligation_type": (
                    obligation.obligation_type
                ),
                "due_date": (
                    obligation.due_date.isoformat()
                    if obligation.due_date
                    else ""
                ),
                "assigned_to": obligation.assigned_to,
                "status": obligation_status,
                "completion_date": (
                    obligation.completion_date.isoformat()
                    if obligation.completion_date
                    else None
                ),
            }
        )

    return {
        "total_obligations": total,
        "pending_obligations": pending,
        "completed_obligations": completed,
        "overdue_obligations": overdue,
        "obligations_by_status": grouped,
        "obligation_records": obligation_records,
    }


# ============================================================
# RENEWAL REPORT
# ============================================================

def get_renewal_summary(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    today = date.today()

    query = db.query(Renewal)

    if start_date:
        query = query.filter(
            Renewal.previous_expiry_date
            >= start_date
        )

    if end_date:
        query = query.filter(
            Renewal.previous_expiry_date
            <= end_date
        )

    renewals = (
        query
        .order_by(Renewal.previous_expiry_date)
        .all()
    )

    upcoming = 0
    expired = 0
    immediate_attention = 0

    renewal_records = []

    for renewal in renewals:

        if renewal.status in {
            "Renewed",
            "Cancelled",
        }:
            continue

        contract = (
            db.query(Contract)
            .filter(
                Contract.id
                == renewal.contract_id
            )
            .first()
        )

        expiry_date = (
            renewal.previous_expiry_date
        )

        days_remaining = None

        if expiry_date:
            days_remaining = (
                expiry_date - today
            ).days

        if (
            expiry_date
            and expiry_date < today
        ):

            expired += 1

        elif (
            expiry_date
            and 0 <= days_remaining <= 30
        ):

            upcoming += 1

            if days_remaining <= 7:
                immediate_attention += 1

        elif expiry_date:

            upcoming += 1

        renewal_records.append(
            {
                "contract_id": renewal.contract_id,
                "contract_number": (
                    contract.contract_number
                    if contract
                    else None
                ),
                "contract_title": (
                    contract.title
                    if contract
                    else None
                ),
                "expiry_date": (
                    expiry_date.isoformat()
                    if expiry_date
                    else None
                ),
                "renewal_date": (
                    renewal.renewal_date.isoformat()
                    if renewal.renewal_date
                    else None
                ),
                "days_remaining": days_remaining,
                "status": renewal.status,
            }
        )

    return {
        "upcoming_renewals": upcoming,
        "expired_contracts": expired,
        "immediate_attention": immediate_attention,
        "renewal_records": renewal_records,
    }


# ============================================================
# COMPLIANCE REPORT
# ============================================================

def get_compliance_summary(
    db: Session,
):
    contracts = (
        db.query(Contract)
        .order_by(Contract.id)
        .all()
    )

    total_contracts = len(contracts)

    compliant = 0
    pending = 0
    delayed = 0
    non_compliant = 0
    high_risk = 0

    compliance_records = []

    for contract in contracts:

        obligations = (
            db.query(Obligation)
            .filter(
                Obligation.contract_id
                == contract.id
            )
            .all()
        )

        result = calculate_contract_compliance(
            contract,
            obligations,
        )

        compliance_status = (
            result.get(
                "compliance_status",
                "Pending",
            )
        )

        risk_level = (
            result.get(
                "risk_level",
                "Low",
            )
        )

        total_obligations = len(
            obligations
        )

        completed_obligations = sum(
            1
            for obligation in obligations
            if obligation.status == "Completed"
        )

        pending_obligations = sum(
            1
            for obligation in obligations
            if obligation.status == "Pending"
            and (
                not obligation.due_date
                or obligation.due_date >= date.today()
            )
        )

        delayed_obligations = sum(
            1
            for obligation in obligations
            if obligation.status == "Delayed"
        )

        overdue_obligations = sum(
            1
            for obligation in obligations
            if obligation.status == "Overdue"
            or (
                obligation.status == "Pending"
                and obligation.due_date
                and obligation.due_date < date.today()
            )
        )

        if total_obligations > 0:
            compliance_score = round(
                (
                    completed_obligations
                    / total_obligations
                ) * 100,
                2,
            )
        else:
            compliance_score = 0.0

        if compliance_status == "Compliant":
            compliant += 1

        elif compliance_status == "Delayed":
            delayed += 1

        elif compliance_status == "Non-Compliant":
            non_compliant += 1

        else:
            pending += 1

        if risk_level == "High":
            high_risk += 1

        compliance_records.append(
            {
                "contract_id": contract.id,
                "contract_number": (
                    contract.contract_number
                ),
                "contract_title": contract.title,
                "total_obligations": total_obligations,
                "completed_obligations": (
                    completed_obligations
                ),
                "pending_obligations": (
                    pending_obligations
                ),
                "delayed_obligations": (
                    delayed_obligations
                ),
                "overdue_obligations": (
                    overdue_obligations
                ),
                "compliance_score": (
                    compliance_score
                ),
                "compliance_status": (
                    compliance_status
                ),
                "risk_level": risk_level,
            }
        )

    if total_contracts:
        compliance_percentage = round(
            (
                compliant
                / total_contracts
            ) * 100,
            2,
        )
    else:
        compliance_percentage = 0.0

    return {
        "total_contracts": total_contracts,
        "compliant_contracts": compliant,
        "pending_contracts": pending,
        "delayed_contracts": delayed,
        "non_compliant_contracts": non_compliant,
        "high_risk_contracts": high_risk,
        "compliance_percentage": (
            compliance_percentage
        ),
        "compliance_records": compliance_records,
    }


# ============================================================
# COMPLETE DASHBOARD
# ============================================================

def get_dashboard_summary(
    db: Session,
):
    contracts = get_contract_summary(db)

    obligations = get_obligation_summary(db)

    renewals = get_renewal_summary(db)

    compliance = get_compliance_summary(db)

    return {
        "contracts": contracts,
        "obligations": obligations,
        "renewals": renewals,
        "compliance": compliance,
    }
