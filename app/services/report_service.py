from datetime import date, timedelta

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.renewal import Renewal
from app.models.user import User


def _contract_statistics(db: Session) -> dict:
    counts = dict(
        db.query(Contract.status, func.count(Contract.id))
        .group_by(Contract.status)
        .all()
    )
    categories = dict(
        db.query(Contract.category, func.count(Contract.id))
        .group_by(Contract.category)
        .order_by(Contract.category)
        .all()
    )

    def count(status: str) -> int:
        return int(counts.get(status, 0))

    return {
        "total": sum(counts.values()),
        "active": count("Active"),
        "draft": count("Draft"),
        "under_review": count("Under Review"),
        "approved": count("Approved"),
        "expired": count("Expired"),
        "terminated": count("Terminated"),
        "by_category": categories,
    }


def _obligation_statistics(db: Session) -> dict:
    today = date.today()
    overdue = case(
        (Obligation.status == "Overdue", 1),
        ((Obligation.status != "Completed") & (Obligation.due_date < today), 1),
        else_=0,
    )
    rows = db.query(
        func.count(Obligation.id),
        func.sum(case((Obligation.status == "Pending", 1), else_=0)),
        func.sum(case((Obligation.status == "In Progress", 1), else_=0)),
        func.sum(case((Obligation.status == "Completed", 1), else_=0)),
        func.sum(case((Obligation.status == "Delayed", 1), else_=0)),
        func.sum(overdue),
    ).one()
    return {
        "total": int(rows[0] or 0),
        "pending": int(rows[1] or 0),
        "in_progress": int(rows[2] or 0),
        "completed": int(rows[3] or 0),
        "delayed": int(rows[4] or 0),
        "overdue": int(rows[5] or 0),
    }


def _renewal_statistics(db: Session, renewal_window_days: int = 90) -> dict:
    counts = dict(
        db.query(Renewal.status, func.count(Renewal.id))
        .group_by(Renewal.status)
        .all()
    )
    today = date.today()
    end_date = today + timedelta(days=renewal_window_days)
    approaching = (
        db.query(Contract)
        .filter(Contract.end_date >= today, Contract.end_date <= end_date)
        .order_by(Contract.end_date)
        .all()
    )
    return {
        "upcoming": int(counts.get("Upcoming", 0)),
        "in_progress": int(counts.get("In Progress", 0)),
        "renewed": int(counts.get("Renewed", 0)),
        "expired": int(counts.get("Expired", 0)),
        "cancelled": int(counts.get("Cancelled", 0)),
        "approaching_expiry": [
            {
                "contract_id": contract.id,
                "contract_number": contract.contract_number,
                "contract_title": contract.title,
                "expiry_date": contract.end_date,
                "days_remaining": (contract.end_date - today).days,
            }
            for contract in approaching
        ],
    }


def _compliance_rows(db: Session) -> list[dict]:
    contracts = db.query(Contract).order_by(Contract.id).all()
    obligation_rows = (
        db.query(
            Obligation.contract_id,
            func.count(Obligation.id),
            func.sum(case((Obligation.status == "Completed", 1), else_=0)),
            func.sum(
                case(
                    (
                        (Obligation.status != "Completed")
                        & (
                            (Obligation.status == "Overdue")
                            | (Obligation.due_date < date.today())
                        ),
                        1,
                    ),
                    else_=0,
                )
            ),
            func.sum(case((Obligation.status == "Delayed", 1), else_=0)),
        )
        .group_by(Obligation.contract_id)
        .all()
    )
    by_contract = {row[0]: row[1:] for row in obligation_rows}
    results = []
    for contract in contracts:
        total, completed, overdue, delayed = by_contract.get(contract.id, (0, 0, 0, 0))
        total = int(total or 0)
        completed = int(completed or 0)
        overdue = int(overdue or 0)
        delayed = int(delayed or 0)
        pending = max(total - completed - overdue - delayed, 0)
        score = round((completed / total) * 100, 2) if total else 0.0
        if overdue:
            status, risk = "Non-Compliant", "High" if overdue >= 2 else "Medium"
        elif delayed:
            status, risk = "Delayed", "Low"
        elif pending:
            status, risk = "Pending", "Low"
        else:
            status, risk = "Compliant", "Low"
        results.append({
            "contract": contract,
            "compliance_status": status,
            "risk_level": risk,
            "compliance_score": score,
            "overdue_obligations": overdue,
        })
    return results


def compliance_statistics(db: Session) -> dict:
    rows = _compliance_rows(db)
    counts = {status: sum(row["compliance_status"] == status for row in rows) for status in ("Compliant", "Pending", "Delayed", "Non-Compliant")}
    return {
        "total_contracts": len(rows),
        "compliant": counts["Compliant"],
        "pending": counts["Pending"],
        "delayed": counts["Delayed"],
        "non_compliant": counts["Non-Compliant"],
        "high_risk": sum(row["risk_level"] == "High" for row in rows),
        "average_score": round(sum(row["compliance_score"] for row in rows) / len(rows), 2) if rows else 0.0,
    }


def dashboard_summary(db: Session) -> dict:
    return {
        "contracts": _contract_statistics(db),
        "obligations": _obligation_statistics(db),
        "renewals": _renewal_statistics(db),
        "compliance": compliance_statistics(db),
    }


def risk_summary(db: Session) -> list[dict]:
    return [
        {
            "contract_id": row["contract"].id,
            "contract_number": row["contract"].contract_number,
            "contract_title": row["contract"].title,
            "risk_level": row["risk_level"],
            "overdue_obligations": row["overdue_obligations"],
            "compliance_score": row["compliance_score"],
        }
        for row in _compliance_rows(db)
        if row["risk_level"] == "High"
    ]


def department_performance() -> dict:
    return {
        "available": False,
        "limitation": "Department data is not present in the current user or contract schema.",
        "departments": [],
    }


def report_rows(db: Session, report_type: str) -> list[dict]:
    if report_type == "contracts":
        rows = db.query(Contract, User.full_name).outerjoin(User, Contract.assigned_to == User.id).all()
        return [{"Contract Number": c.contract_number, "Title": c.title, "Category": c.category, "Status": c.status, "Start Date": c.start_date, "End Date": c.end_date, "Assigned User": name or ""} for c, name in rows]
    if report_type == "obligations":
        rows = (
            db.query(Obligation, Contract.contract_number, User.full_name)
            .select_from(Obligation)
            .join(Contract, Obligation.contract_id == Contract.id)
            .outerjoin(User, Obligation.assigned_to == User.id)
            .all()
        )
        return [{"Contract": number, "Obligation Title": o.title, "Obligation Type": o.obligation_type, "Assigned User": name or "", "Due Date": o.due_date, "Status": o.status, "Completion Date": o.completion_date} for o, number, name in rows]
    if report_type == "renewals":
        rows = (
            db.query(Renewal, Contract.contract_number, User.full_name)
            .select_from(Renewal)
            .join(Contract, Renewal.contract_id == Contract.id)
            .outerjoin(User, Renewal.assigned_to == User.id)
            .all()
        )
        return [{"Contract": number, "Previous Expiry Date": r.previous_expiry_date, "Renewal Date": r.renewal_date, "New Expiry Date": r.new_expiry_date, "Renewal Status": r.status, "Assigned User": name or ""} for r, number, name in rows]
    rows = db.query(Contract, User.full_name).outerjoin(User, Contract.assigned_to == User.id).all()
    compliance = {row["contract"].id: row for row in _compliance_rows(db)}
    return [{"Contract": c.contract_number, "Compliance Status": compliance[c.id]["compliance_status"], "Compliance Score": compliance[c.id]["compliance_score"], "Overdue Obligations": compliance[c.id]["overdue_obligations"], "Risk Level": compliance[c.id]["risk_level"], "Evaluation Date": date.today()} for c, _ in rows]