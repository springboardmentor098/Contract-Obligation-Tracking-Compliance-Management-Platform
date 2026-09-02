from datetime import date
from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.obligation import Obligation


# ============================================================
# COMPLIANCE STATUSES
# ============================================================

COMPLIANCE_STATUSES = {
    "Compliant",
    "Pending",
    "Delayed",
    "Non-Compliant",
}


# ============================================================
# RISK LEVELS
# ============================================================

RISK_LEVELS = {
    "Low",
    "Medium",
    "High",
}


# ============================================================
# CALCULATE COMPLIANCE FOR ONE CONTRACT
# ============================================================

def calculate_contract_compliance(
    db: Session,
    contract_id: int
):
    """
    Calculate compliance for a single contract.
    """

    # --------------------------------------------------------
    # Check contract exists
    # --------------------------------------------------------

    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        return None

    # --------------------------------------------------------
    # Get all obligations for this contract
    # --------------------------------------------------------

    obligations = (
        db.query(Obligation)
        .filter(Obligation.contract_id == contract_id)
        .all()
    )

    total_obligations = len(obligations)

    # --------------------------------------------------------
    # No obligations
    # --------------------------------------------------------

    if total_obligations == 0:

        return {
            "contract_id": contract_id,
            "total_obligations": 0,
            "completed_obligations": 0,
            "pending_obligations": 0,
            "delayed_obligations": 0,
            "overdue_obligations": 0,
            "compliance_score": 0.0,
            "compliance_status": "Pending",
            "risk_level": "Low",
        }

    # --------------------------------------------------------
    # Counters
    # --------------------------------------------------------

    completed_obligations = 0
    pending_obligations = 0
    delayed_obligations = 0
    overdue_obligations = 0

    today = date.today()

    # --------------------------------------------------------
    # Evaluate obligations
    # --------------------------------------------------------

    for obligation in obligations:

        # Completed
        if obligation.status == "Completed":

            completed_obligations += 1

        # Overdue
        elif (
            obligation.status == "Overdue"
            or (
                obligation.status != "Completed"
                and obligation.due_date < today
            )
        ):

            overdue_obligations += 1

        # Delayed
        elif obligation.status == "Delayed":

            delayed_obligations += 1

        # Pending / In Progress
        elif obligation.status in (
            "Pending",
            "In Progress",
        ):

            pending_obligations += 1

        # Unknown status
        else:

            pending_obligations += 1

    # --------------------------------------------------------
    # Compliance score
    # --------------------------------------------------------

    compliance_score = (
        completed_obligations
        / total_obligations
    ) * 100

    # --------------------------------------------------------
    # Compliance status
    # --------------------------------------------------------

    if overdue_obligations > 0:

        compliance_status = "Non-Compliant"

    elif delayed_obligations > 0:

        compliance_status = "Delayed"

    elif pending_obligations > 0:

        compliance_status = "Pending"

    else:

        compliance_status = "Compliant"

    # --------------------------------------------------------
    # Risk level
    #
    # 0 overdue  -> Low
    # 1 overdue  -> Medium
    # 2+ overdue -> High
    # --------------------------------------------------------

    if overdue_obligations >= 2:

        risk_level = "High"

    elif overdue_obligations == 1:

        risk_level = "Medium"

    else:

        risk_level = "Low"

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "contract_id": contract_id,
        "total_obligations": total_obligations,
        "completed_obligations": completed_obligations,
        "pending_obligations": pending_obligations,
        "delayed_obligations": delayed_obligations,
        "overdue_obligations": overdue_obligations,
        "compliance_score": round(
            compliance_score,
            2
        ),
        "compliance_status": compliance_status,
        "risk_level": risk_level,
    }


# ============================================================
# CALCULATE ALL CONTRACT COMPLIANCE
# ============================================================

def calculate_all_contract_compliance(
    db: Session
):
    """
    Calculate compliance for all contracts.
    """

    contracts = db.query(Contract).all()

    results = []

    for contract in contracts:

        result = calculate_contract_compliance(
            db,
            contract.id
        )

        if result is not None:
            results.append(result)

    return results


# ============================================================
# COMPLIANCE SUMMARY
# ============================================================

def calculate_compliance_summary(
    db: Session
):
    """
    Calculate overall compliance summary.
    """

    results = calculate_all_contract_compliance(db)

    total_contracts = len(results)

    compliant_contracts = 0
    pending_contracts = 0
    delayed_contracts = 0
    non_compliant_contracts = 0
    high_risk_contracts = 0

    for result in results:

        if result["compliance_status"] == "Compliant":
            compliant_contracts += 1

        elif result["compliance_status"] == "Pending":
            pending_contracts += 1

        elif result["compliance_status"] == "Delayed":
            delayed_contracts += 1

        elif result["compliance_status"] == "Non-Compliant":
            non_compliant_contracts += 1

        if result["risk_level"] == "High":
            high_risk_contracts += 1

    # --------------------------------------------------------
    # Average score
    # --------------------------------------------------------

    if total_contracts > 0:

        average_score = (
            sum(
                result["compliance_score"]
                for result in results
            )
            / total_contracts
        )

    else:

        average_score = 0.0

    return {
        "total_contracts": total_contracts,
        "compliant_contracts": compliant_contracts,
        "pending_contracts": pending_contracts,
        "delayed_contracts": delayed_contracts,
        "non_compliant_contracts": non_compliant_contracts,
        "high_risk_contracts": high_risk_contracts,
        "average_compliance_score": round(
            average_score,
            2
        ),
    }


# ============================================================
# GET NON-COMPLIANT CONTRACTS
# ============================================================

def get_non_compliant_contracts(
    db: Session
):
    """
    Return all non-compliant contracts.
    """

    results = calculate_all_contract_compliance(db)

    return [
        result
        for result in results
        if result["compliance_status"]
        == "Non-Compliant"
    ]


# ============================================================
# GET HIGH-RISK CONTRACTS
# ============================================================

def get_high_risk_contracts(
    db: Session
):
    """
    Return all high-risk contracts.
    """

    results = calculate_all_contract_compliance(db)

    return [
        result
        for result in results
        if result["risk_level"] == "High"
    ]

def get_compliance_history(
    db: Session,
    contract_id: int
):
    from app.models.compliance import Compliance

    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        return None

    return (
        db.query(Compliance)
        .filter(
            Compliance.contract_id == contract_id
        )
        .order_by(
            Compliance.evaluated_at.desc()
        )
        .all()
    )