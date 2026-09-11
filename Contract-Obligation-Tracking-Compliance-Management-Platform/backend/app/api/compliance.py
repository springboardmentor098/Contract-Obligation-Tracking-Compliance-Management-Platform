from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.user import User

from app.core.security import get_current_user

from app.schemas.compliance import (
    ComplianceResponse,
    ComplianceSummaryResponse,
    RiskInformationResponse,
)

from app.services.compliance_service import (
    calculate_contract_compliance,
)


router = APIRouter(
    prefix="/compliance",
    tags=["Compliance"],
)


# ============================================================
# Authorization helpers
# ============================================================

MANAGER_ROLES = {
    "admin",
    "manager",
    "contract_manager",
    "Admin",
    "Manager",
    "Contract Manager",
}


def is_manager(user: User) -> bool:
    return getattr(user, "role", None) in MANAGER_ROLES


# ============================================================
# Contract access helper
# ============================================================

def get_contract_or_404(
    db: Session,
    contract_id: int,
) -> Contract:

    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found",
        )

    return contract


# ============================================================
# GET /compliance
# ============================================================

@router.get(
    "",
    response_model=list[ComplianceResponse],
)
def get_all_compliance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    contracts = db.query(Contract).all()

    results = []

    for contract in contracts:

        obligations = (
            db.query(Obligation)
            .filter(
                Obligation.contract_id == contract.id
            )
            .all()
        )

        compliance = calculate_contract_compliance(
            contract,
            obligations,
        )

        results.append(compliance)

    return results


# ============================================================
# GET /compliance/summary
# IMPORTANT: Must appear before parameterized routes
# ============================================================

@router.get(
    "/summary",
    response_model=ComplianceSummaryResponse,
)
def get_compliance_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    contracts = db.query(Contract).all()

    summary = {
        "total_contracts": len(contracts),
        "compliant_contracts": 0,
        "pending_contracts": 0,
        "delayed_contracts": 0,
        "non_compliant_contracts": 0,
        "high_risk_contracts": 0,
    }

    for contract in contracts:

        obligations = (
            db.query(Obligation)
            .filter(
                Obligation.contract_id == contract.id
            )
            .all()
        )

        compliance = calculate_contract_compliance(
            contract,
            obligations,
        )

        status = compliance["compliance_status"]

        if status == "Compliant":
            summary["compliant_contracts"] += 1

        elif status == "Pending":
            summary["pending_contracts"] += 1

        elif status == "Delayed":
            summary["delayed_contracts"] += 1

        elif status == "Non-Compliant":
            summary["non_compliant_contracts"] += 1

        elif status == "High Risk":
            summary["high_risk_contracts"] += 1

    return summary


# ============================================================
# GET /compliance/non-compliant
# ============================================================

@router.get(
    "/non-compliant",
    response_model=list[ComplianceResponse],
)
def get_non_compliant_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    contracts = db.query(Contract).all()

    results = []

    for contract in contracts:

        obligations = (
            db.query(Obligation)
            .filter(
                Obligation.contract_id == contract.id
            )
            .all()
        )

        compliance = calculate_contract_compliance(
            contract,
            obligations,
        )

        if compliance["compliance_status"] in {
            "Non-Compliant",
            "High Risk",
        }:
            results.append(compliance)

    return results


# ============================================================
# GET /compliance/high-risk
# ============================================================

@router.get(
    "/high-risk",
    response_model=list[RiskInformationResponse],
)
def get_high_risk_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    contracts = db.query(Contract).all()

    results = []

    for contract in contracts:

        obligations = (
            db.query(Obligation)
            .filter(
                Obligation.contract_id == contract.id
            )
            .all()
        )

        compliance = calculate_contract_compliance(
            contract,
            obligations,
        )

        if compliance["risk_level"] == "High":

            results.append(
                {
                    "contract_id": compliance["contract_id"],
                    "contract_number": compliance["contract_number"],
                    "risk_level": compliance["risk_level"],
                    "overdue_obligations": compliance[
                        "overdue_obligations"
                    ],
                    "delayed_obligations": compliance[
                        "delayed_obligations"
                    ],
                    "compliance_score": compliance[
                        "compliance_score"
                    ],
                }
            )

    return results