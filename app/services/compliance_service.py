from app.models.obligation import Obligation


def calculate_compliance(contract):
    """
    Calculate compliance statistics for a contract.
    """

    obligations = contract.obligations

    total = len(obligations)

    if total == 0:
        return {
            "compliance_score": 100,
            "status": "Compliant",
            "risk_level": "Low",
            "total_obligations": 0,
            "completed": 0,
            "pending": 0,
            "overdue": 0
        }

    completed = len([
        o for o in obligations
        if o.status == "Completed"
    ])

    pending = len([
        o for o in obligations
        if o.status in ["Pending", "In Progress"]
    ])

    overdue = len([
        o for o in obligations
        if o.status in ["Overdue", "Delayed"]
    ])

    score = round((completed / total) * 100)

    if score >= 90:
        status = "Compliant"
        risk = "Low"
    elif score >= 70:
        status = "Partially Compliant"
        risk = "Medium"
    else:
        status = "Non-Compliant"
        risk = "High"

    return {
        "compliance_score": score,
        "status": status,
        "risk_level": risk,
        "total_obligations": total,
        "completed": completed,
        "pending": pending,
        "overdue": overdue
    }