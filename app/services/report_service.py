from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.renewal import Renewal


def get_dashboard_summary(db: Session):
    # -----------------------------
    # Contract statistics
    # -----------------------------
    total_contracts = db.query(Contract).count()

    active_contracts = (
        db.query(Contract)
        .filter(Contract.status == "Active")
        .count()
    )

    draft_contracts = (
        db.query(Contract)
        .filter(Contract.status == "Draft")
        .count()
    )

    under_review_contracts = (
        db.query(Contract)
        .filter(Contract.status == "Under Review")
        .count()
    )

    expired_contracts = (
        db.query(Contract)
        .filter(Contract.status == "Expired")
        .count()
    )

    # -----------------------------
    # Obligation statistics
    # -----------------------------
    total_obligations = db.query(Obligation).count()

    pending_obligations = (
        db.query(Obligation)
        .filter(Obligation.status == "pending")
        .count()
    )

    overdue_obligations = (
        db.query(Obligation)
        .filter(Obligation.status == "overdue")
        .count()
    )

    completed_obligations = (
        db.query(Obligation)
        .filter(Obligation.status == "completed")
        .count()
    )

    # -----------------------------
    # Renewal statistics
    # -----------------------------
    total_renewals = db.query(Renewal).count()

    today = date.today()
    next_30_days = today + timedelta(days=30)

    upcoming_renewals = (
        db.query(Renewal)
        .filter(
            Renewal.renewal_date >= today,
            Renewal.renewal_date <= next_30_days,
            Renewal.status == "upcoming",
        )
        .count()
    )

    completed_renewals = (
        db.query(Renewal)
        .filter(Renewal.status == "completed")
        .count()
    )

    # -----------------------------
    # Compliance / risk indicators
    #
    # These indicators are derived
    # from obligation status because
    # there is currently no separate
    # compliance/risk model.
    # -----------------------------
    problem_obligation_contract_ids = {
        contract_id
        for (contract_id,) in (
            db.query(Obligation.contract_id)
            .filter(
                Obligation.status.in_(["pending", "overdue"])
            )
            .distinct()
            .all()
        )
    }

    overdue_contract_ids = {
        contract_id
        for (contract_id,) in (
            db.query(Obligation.contract_id)
            .filter(Obligation.status == "overdue")
            .distinct()
            .all()
        )
    }

    high_risk_contract_ids = {
        contract_id
        for (contract_id,) in (
            db.query(Obligation.contract_id)
            .filter(
                Obligation.status == "overdue",
                Obligation.priority == "high",
            )
            .distinct()
            .all()
        )
    }

    compliant_contracts = (
        db.query(Contract).count()
        - len(problem_obligation_contract_ids)
    )

    non_compliant_contracts = len(overdue_contract_ids)

    high_risk_contracts = len(high_risk_contract_ids)

    return {
        "contracts": {
            "total": total_contracts,
            "active": active_contracts,
            "draft": draft_contracts,
            "under_review": under_review_contracts,
            "expired": expired_contracts,
        },
        "obligations": {
            "total": total_obligations,
            "pending": pending_obligations,
            "overdue": overdue_obligations,
            "completed": completed_obligations,
        },
        "renewals": {
            "total": total_renewals,
            "upcoming": upcoming_renewals,
            "completed": completed_renewals,
        },
        "compliance": {
            "compliant_contracts": compliant_contracts,
            "non_compliant_contracts": non_compliant_contracts,
            "high_risk_contracts": high_risk_contracts,
        },
    }


def get_contract_analytics(db: Session):
    today = date.today()
    next_30_days = today + timedelta(days=30)
    next_90_days = today + timedelta(days=90)

    contracts = db.query(Contract).all()

    by_status = {}
    by_category = {}
    by_counterparty = {}

    for contract in contracts:
        status = contract.status or "Unknown"
        category = contract.category or "Unknown"
        counterparty = contract.counterparty_name or "Unknown"

        by_status[status] = by_status.get(status, 0) + 1
        by_category[category] = by_category.get(category, 0) + 1
        by_counterparty[counterparty] = (
            by_counterparty.get(counterparty, 0) + 1
        )

    expiring_next_30_days = (
        db.query(Contract)
        .filter(
            Contract.end_date.isnot(None),
            Contract.end_date >= today,
            Contract.end_date <= next_30_days,
        )
        .count()
    )

    expiring_next_90_days = (
        db.query(Contract)
        .filter(
            Contract.end_date.isnot(None),
            Contract.end_date >= today,
            Contract.end_date <= next_90_days,
        )
        .count()
    )

    return {
        "contracts": {
            "total": len(contracts),
            "by_status": by_status,
            "by_category": by_category,
            "by_counterparty": by_counterparty,
            "expiring_next_30_days": expiring_next_30_days,
            "expiring_next_90_days": expiring_next_90_days,
        }
    }

def get_obligation_analytics(db: Session):
    today = date.today()
    next_7_days = today + timedelta(days=7)
    next_30_days = today + timedelta(days=30)

    obligations = db.query(Obligation).all()

    by_status = {}
    by_priority = {}
    by_responsible_party = {}

    for obligation in obligations:
        obligation_status = obligation.status or "Unknown"
        priority = obligation.priority or "Unknown"
        responsible_party = (
            obligation.responsible_party or "Unassigned"
        )

        by_status[obligation_status] = (
            by_status.get(obligation_status, 0) + 1
        )

        by_priority[priority] = (
            by_priority.get(priority, 0) + 1
        )

        by_responsible_party[responsible_party] = (
            by_responsible_party.get(responsible_party, 0) + 1
        )

    overdue = (
        db.query(Obligation)
        .filter(Obligation.status == "overdue")
        .count()
    )

    due_next_7_days = (
        db.query(Obligation)
        .filter(
            Obligation.due_date.isnot(None),
            Obligation.due_date >= today,
            Obligation.due_date <= next_7_days,
            Obligation.status != "completed",
        )
        .count()
    )

    due_next_30_days = (
        db.query(Obligation)
        .filter(
            Obligation.due_date.isnot(None),
            Obligation.due_date >= today,
            Obligation.due_date <= next_30_days,
            Obligation.status != "completed",
        )
        .count()
    )

    return {
        "obligations": {
            "total": len(obligations),
            "by_status": by_status,
            "by_priority": by_priority,
            "by_responsible_party": by_responsible_party,
            "overdue": overdue,
            "due_next_7_days": due_next_7_days,
            "due_next_30_days": due_next_30_days,
        }
    }

def get_renewal_analytics(db: Session):
    today = date.today()
    next_7_days = today + timedelta(days=7)
    next_30_days = today + timedelta(days=30)
    next_90_days = today + timedelta(days=90)

    renewals = db.query(Renewal).all()

    by_status = {}
    by_contract = {}

    for renewal in renewals:
        renewal_status = renewal.status or "Unknown"
        by_status[renewal_status] = (
            by_status.get(renewal_status, 0) + 1
        )

        contract = (
            db.query(Contract)
            .filter(Contract.id == renewal.contract_id)
            .first()
        )

        if contract:
            contract_name = (
                contract.contract_number
                or contract.title
                or str(contract.id)
            )
        else:
            contract_name = str(renewal.contract_id)

        by_contract[contract_name] = (
            by_contract.get(contract_name, 0) + 1
        )

    due_next_7_days = (
        db.query(Renewal)
        .filter(
            Renewal.renewal_date >= today,
            Renewal.renewal_date <= next_7_days,
            Renewal.status != "completed",
        )
        .count()
    )

    due_next_30_days = (
        db.query(Renewal)
        .filter(
            Renewal.renewal_date >= today,
            Renewal.renewal_date <= next_30_days,
            Renewal.status != "completed",
        )
        .count()
    )

    due_next_90_days = (
        db.query(Renewal)
        .filter(
            Renewal.renewal_date >= today,
            Renewal.renewal_date <= next_90_days,
            Renewal.status != "completed",
        )
        .count()
    )

    overdue = (
        db.query(Renewal)
        .filter(
            Renewal.renewal_date < today,
            Renewal.status != "completed",
        )
        .count()
    )

    return {
        "renewals": {
            "total": len(renewals),
            "by_status": by_status,
            "due_next_7_days": due_next_7_days,
            "due_next_30_days": due_next_30_days,
            "due_next_90_days": due_next_90_days,
            "overdue": overdue,
            "by_contract": by_contract,
        }
    }

def get_compliance_analytics(db: Session):
    total_contracts = db.query(Contract).count()

    # Find contracts that have pending or overdue obligations.
    problem_contract_ids = {
        row[0]
        for row in (
            db.query(Obligation.contract_id)
            .filter(
                Obligation.contract_id.isnot(None),
                func.lower(Obligation.status).in_(["pending", "overdue"])
            )
            .distinct()
            .all()
        )
    }

    # Contracts with overdue obligations are considered non-compliant.
    non_compliant_contract_ids = {
        row[0]
        for row in (
            db.query(Obligation.contract_id)
            .filter(
                Obligation.contract_id.isnot(None),
                func.lower(Obligation.status) == "overdue"
            )
            .distinct()
            .all()
        )
    }

    # Contracts with high-priority overdue obligations are high-risk.
    high_risk_contract_ids = {
        row[0]
        for row in (
            db.query(Obligation.contract_id)
            .filter(
                Obligation.contract_id.isnot(None),
                func.lower(Obligation.status) == "overdue",
                func.lower(Obligation.priority) == "high"
            )
            .distinct()
            .all()
        )
    }

    compliant_contracts = max(
        total_contracts - len(problem_contract_ids),
        0
    )

    non_compliant_contracts = len(non_compliant_contract_ids)
    high_risk_contracts = len(high_risk_contract_ids)

    compliance_rate = (
        round((compliant_contracts / total_contracts) * 100, 2)
        if total_contracts
        else 0.0
    )

    overdue_obligations = (
        db.query(Obligation)
        .filter(func.lower(Obligation.status) == "overdue")
        .count()
    )

    high_priority_overdue_obligations = (
        db.query(Obligation)
        .filter(
            func.lower(Obligation.status) == "overdue",
            func.lower(Obligation.priority) == "high"
        )
        .count()
    )

    return {
        "compliance": {
            "total_contracts": total_contracts,
            "compliant_contracts": compliant_contracts,
            "non_compliant_contracts": non_compliant_contracts,
            "high_risk_contracts": high_risk_contracts,
            "compliance_rate": compliance_rate,
            "overdue_obligations": overdue_obligations,
            "high_priority_overdue_obligations": high_priority_overdue_obligations,
        }
    }
