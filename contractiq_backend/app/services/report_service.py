from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.renewal import Renewal
from app.services.compliance_service import calculate_contract_compliance


# ============================================================
# CONTRACT REPORT
# ============================================================

def get_contract_statistics(db: Session):
    total = db.query(Contract).count()

    active = (
        db.query(Contract)
        .filter(Contract.status == "Active")
        .count()
    )

    draft = (
        db.query(Contract)
        .filter(Contract.status == "Draft")
        .count()
    )

    under_review = (
        db.query(Contract)
        .filter(Contract.status == "Under Review")
        .count()
    )

    approved = (
        db.query(Contract)
        .filter(Contract.status == "Approved")
        .count()
    )

    expired = (
        db.query(Contract)
        .filter(Contract.status == "Expired")
        .count()
    )

    terminated = (
        db.query(Contract)
        .filter(Contract.status == "Terminated")
        .count()
    )

    return {
        "total_contracts": total,
        "active_contracts": active,
        "draft_contracts": draft,
        "under_review_contracts": under_review,
        "approved_contracts": approved,
        "expired_contracts": expired,
        "terminated_contracts": terminated,
    }


# ============================================================
# OBLIGATION REPORT
# ============================================================

def get_obligation_statistics(db: Session):
    obligations = db.query(Obligation).all()

    total = len(obligations)
    completed = 0
    pending = 0
    overdue = 0
    delayed = 0

    today = date.today()

    for obligation in obligations:
        if obligation.status == "Completed":
            completed += 1

        elif obligation.status == "Delayed":
            delayed += 1

        elif obligation.status == "Overdue":
            overdue += 1

        elif (
            obligation.status == "Pending"
            and obligation.due_date < today
        ):
            overdue += 1

        else:
            pending += 1

    completion_rate = (
        round((completed / total) * 100, 2)
        if total > 0
        else 0
    )

    return {
        "total_obligations": total,
        "completed_obligations": completed,
        "pending_obligations": pending,
        "overdue_obligations": overdue,
        "delayed_obligations": delayed,
        "completion_rate": completion_rate,
    }


# ============================================================
# RENEWAL REPORT
# ============================================================

def get_renewal_statistics(db: Session):
    total = db.query(Renewal).count()

    upcoming = (
        db.query(Renewal)
        .filter(Renewal.status == "Upcoming")
        .count()
    )

    in_progress = (
        db.query(Renewal)
        .filter(Renewal.status == "In Progress")
        .count()
    )

    renewed = (
        db.query(Renewal)
        .filter(Renewal.status == "Renewed")
        .count()
    )

    expired = (
        db.query(Renewal)
        .filter(Renewal.status == "Expired")
        .count()
    )

    cancelled = (
        db.query(Renewal)
        .filter(Renewal.status == "Cancelled")
        .count()
    )

    return {
        "total_renewals": total,
        "upcoming_renewals": upcoming,
        "in_progress_renewals": in_progress,
        "renewed_renewals": renewed,
        "expired_renewals": expired,
        "cancelled_renewals": cancelled,
    }


# ============================================================
# UPCOMING RENEWALS
# ============================================================

def get_upcoming_renewals(
    db: Session,
    days: int = 30
):
    today = date.today()
    end_date = today + timedelta(days=days)

    return (
        db.query(Renewal)
        .filter(
            Renewal.renewal_date >= today,
            Renewal.renewal_date <= end_date,
            Renewal.status == "Upcoming"
        )
        .order_by(Renewal.renewal_date.asc())
        .all()
    )


# ============================================================
# OVERDUE OBLIGATIONS
# ============================================================

def get_overdue_obligations(db: Session):
    today = date.today()

    return (
        db.query(Obligation)
        .filter(
            Obligation.due_date < today,
            Obligation.status != "Completed"
        )
        .order_by(Obligation.due_date.asc())
        .all()
    )


# ============================================================
# COMPLIANCE REPORT
# ============================================================

def get_compliance_statistics(db: Session):
    contracts = db.query(Contract).all()

    total_contracts = len(contracts)

    compliant = 0
    pending = 0
    delayed = 0
    non_compliant = 0
    high_risk = 0

    scores = []

    for contract in contracts:
        result = calculate_contract_compliance(
            contract.id,
            db
        )

        status = result["compliance_status"]
        risk = result["risk_level"]
        score = result["compliance_score"]

        scores.append(score)

        if status == "Compliant":
            compliant += 1

        elif status == "Pending":
            pending += 1

        elif status == "Delayed":
            delayed += 1

        elif status in {"Non-Compliant", "High Risk"}:
            non_compliant += 1

        if risk == "High":
            high_risk += 1

    average_score = (
        round(sum(scores) / len(scores), 2)
        if scores
        else 0
    )

    return {
        "total_contracts": total_contracts,
        "compliant_contracts": compliant,
        "pending_contracts": pending,
        "delayed_contracts": delayed,
        "non_compliant_contracts": non_compliant,
        "high_risk_contracts": high_risk,
        "average_compliance_score": average_score,
    }


# ============================================================
# RISK REPORT
# ============================================================

def get_risk_summary(db: Session):
    contracts = db.query(Contract).all()

    low = 0
    medium = 0
    high = 0

    for contract in contracts:
        result = calculate_contract_compliance(
            contract.id,
            db
        )

        risk = result["risk_level"]

        if risk == "High":
            high += 1

        elif risk == "Medium":
            medium += 1

        else:
            low += 1

    return {
        "low_risk_contracts": low,
        "medium_risk_contracts": medium,
        "high_risk_contracts": high,
        "total_risk_contracts": low + medium + high,
    }


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

def get_dashboard_summary(db: Session):
    contract_stats = get_contract_statistics(db)
    obligation_stats = get_obligation_statistics(db)
    renewal_stats = get_renewal_statistics(db)
    compliance_stats = get_compliance_statistics(db)
    risk_stats = get_risk_summary(db)

    return {
        "total_contracts": contract_stats["total_contracts"],
        "active_contracts": contract_stats["active_contracts"],
        "total_obligations": obligation_stats["total_obligations"],
        "pending_obligations": obligation_stats["pending_obligations"],
        "overdue_obligations": obligation_stats["overdue_obligations"],
        "upcoming_renewals": renewal_stats["upcoming_renewals"],
        "high_risk_contracts": risk_stats["high_risk_contracts"],
        "compliance_score": compliance_stats[
            "average_compliance_score"
        ],
    }


# ============================================================
# DEPARTMENT PERFORMANCE
# ============================================================
def get_department_performance(db: Session):
    departments = (
        db.query(Contract.department)
        .filter(Contract.department.isnot(None))
        .distinct()
        .all()
    )

    results = []

    for (department,) in departments:
        contracts = (
            db.query(Contract)
            .filter(Contract.department == department)
            .all()
        )

        contract_ids = [contract.id for contract in contracts]

        obligations = []
        if contract_ids:
            obligations = (
                db.query(Obligation)
                .filter(Obligation.contract_id.in_(contract_ids))
                .all()
            )

        total_obligations = len(obligations)

        completed_obligations = sum(
            1
            for obligation in obligations
            if obligation.status == "Completed"
        )

        today = date.today()

        overdue_obligations = sum(
            1
            for obligation in obligations
            if (
                obligation.status != "Completed"
                and obligation.due_date < today
            )
        )

        compliance_score = (
            round(
                (completed_obligations / total_obligations) * 100,
                2
            )
            if total_obligations > 0
            else 0
        )

        results.append({
            "department": department,
            "total_contracts": len(contracts),
            "total_obligations": total_obligations,
            "completed_obligations": completed_obligations,
            "overdue_obligations": overdue_obligations,
            "compliance_score": compliance_score
        })

    return results