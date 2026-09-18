from datetime import date, datetime, timezone
from typing import Any

from app.models.contract import Contract
from app.models.obligation import Obligation


# ============================================================
# Status helpers
# ============================================================

COMPLETED_STATUSES = {
    "Completed",
    "completed",
}

PENDING_STATUSES = {
    "Pending",
    "pending",
}

DELAYED_STATUSES = {
    "Delayed",
    "delayed",
}

OVERDUE_STATUSES = {
    "Overdue",
    "overdue",
}


# ============================================================
# Obligation status classification
# ============================================================

def classify_obligation(obligation: Obligation) -> str:
    """
    Determine the compliance category of an obligation.

    Existing explicit statuses are respected first.
    Due-date information is used for basic overdue detection.
    """

    status = getattr(obligation, "status", None)

    if status in COMPLETED_STATUSES:
        return "Completed"

    if status in OVERDUE_STATUSES:
        return "Overdue"

    if status in DELAYED_STATUSES:
        return "Delayed"

    if status in PENDING_STATUSES:
        due_date = getattr(obligation, "due_date", None)

        if due_date is not None and due_date < date.today():
            return "Overdue"

        return "Pending"

    # Unknown/in-progress obligations are treated as pending
    # unless their due date has passed.
    due_date = getattr(obligation, "due_date", None)

    if due_date is not None and due_date < date.today():
        return "Overdue"

    return "Pending"


# ============================================================
# Risk calculation
# ============================================================

def determine_risk_level(
    total_obligations: int,
    overdue_obligations: int,
    delayed_obligations: int,
) -> str:

    if overdue_obligations >= 2:
        return "High"

    if overdue_obligations == 1:
        return "Medium"

    if delayed_obligations >= 2:
        return "Medium"

    return "Low"


# ============================================================
# Compliance status calculation
# ============================================================

def determine_compliance_status(
    total_obligations: int,
    completed_obligations: int,
    pending_obligations: int,
    delayed_obligations: int,
    overdue_obligations: int,
    risk_level: str,
) -> str:

    if total_obligations == 0:
        return "Pending"

    if overdue_obligations >= 2:
        return "High Risk"

    if overdue_obligations > 0:
        return "Non-Compliant"

    if delayed_obligations > 0:
        return "Delayed"

    if pending_obligations > 0:
        return "Pending"

    if completed_obligations == total_obligations:
        return "Compliant"

    return "Pending"


# ============================================================
# Main compliance evaluator
# ============================================================

def calculate_contract_compliance(
    contract: Contract,
    obligations: list[Obligation],
) -> dict[str, Any]:

    total = len(obligations)

    completed = 0
    pending = 0
    delayed = 0
    overdue = 0

    for obligation in obligations:

        category = classify_obligation(obligation)

        if category == "Completed":
            completed += 1

        elif category == "Delayed":
            delayed += 1

        elif category == "Overdue":
            overdue += 1

        else:
            pending += 1

    # Compliance score
    if total == 0:
        score = 0.0
    else:
        score = round((completed / total) * 100, 2)

    risk_level = determine_risk_level(
        total_obligations=total,
        overdue_obligations=overdue,
        delayed_obligations=delayed,
    )

    compliance_status = determine_compliance_status(
        total_obligations=total,
        completed_obligations=completed,
        pending_obligations=pending,
        delayed_obligations=delayed,
        overdue_obligations=overdue,
        risk_level=risk_level,
    )

    return {
        "contract_id": contract.id,
        "contract_number": getattr(contract, "contract_number", None),
        "compliance_status": compliance_status,
        "compliance_score": score,
        "total_obligations": total,
        "completed_obligations": completed,
        "pending_obligations": pending,
        "delayed_obligations": delayed,
        "overdue_obligations": overdue,
        "risk_level": risk_level,
        "evaluated_at": datetime.now(timezone.utc),
    }