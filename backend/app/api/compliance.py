from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.contract import Contract
from backend.app.core.auth import get_current_user
from backend.app.schemas.compliance import (
    ComplianceResponse,
    ComplianceSummary,
    ComplianceRiskResponse
)
from backend.app.services.compliance_service import (
    calculate_contract_compliance
)


router = APIRouter(
    prefix="/compliance",
    tags=["Compliance"]
)


# ============================================================
# GET CONTRACT COMPLIANCE
# ============================================================

@router.get(
    "/contracts/{contract_id}/compliance",
    response_model=ComplianceResponse
)
def get_contract_compliance(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return calculate_contract_compliance(
        contract,
        db
    )


# ============================================================
# GET ALL COMPLIANCE RECORDS
# ============================================================

@router.get(
    "",
    response_model=list[ComplianceResponse]
)
def get_all_compliance(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    contracts = db.query(Contract).all()

    compliance_records = []

    for contract in contracts:

        result = calculate_contract_compliance(
            contract,
            db
        )

        compliance_records.append(result)

    return compliance_records


# ============================================================
# GET COMPLIANCE SUMMARY
# ============================================================

@router.get(
    "/summary",
    response_model=ComplianceSummary
)
def get_compliance_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    contracts = db.query(Contract).all()

    total_contracts = len(contracts)

    compliant_contracts = 0
    pending_contracts = 0
    delayed_contracts = 0
    non_compliant_contracts = 0
    high_risk_contracts = 0

    for contract in contracts:

        result = calculate_contract_compliance(
            contract,
            db
        )

        compliance_status = result["compliance_status"]
        risk_level = result["risk_level"]

        if compliance_status == "Compliant":
            compliant_contracts += 1

        elif compliance_status == "Pending":
            pending_contracts += 1

        elif compliance_status == "Delayed":
            delayed_contracts += 1

        elif compliance_status == "Non-Compliant":
            non_compliant_contracts += 1

        if risk_level == "High":
            high_risk_contracts += 1

    return {
        "total_contracts": total_contracts,
        "compliant_contracts": compliant_contracts,
        "pending_contracts": pending_contracts,
        "delayed_contracts": delayed_contracts,
        "non_compliant_contracts": non_compliant_contracts,
        "high_risk_contracts": high_risk_contracts
    }


# ============================================================
# GET NON-COMPLIANT CONTRACTS
# ============================================================

@router.get(
    "/non-compliant",
    response_model=list[ComplianceRiskResponse]
)
def get_non_compliant_contracts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    contracts = db.query(Contract).all()

    results = []

    for contract in contracts:

        result = calculate_contract_compliance(
            contract,
            db
        )

        if result["compliance_status"] == "Non-Compliant":

            results.append({
                "contract_id": result["contract_id"],
                "contract_number": result["contract_number"],
                "compliance_status": result["compliance_status"],
                "compliance_score": result["compliance_score"],
                "overdue_obligations": result["overdue_obligations"],
                "risk_level": result["risk_level"]
            })

    return results


# ============================================================
# GET HIGH-RISK CONTRACTS
# ============================================================

@router.get(
    "/high-risk",
    response_model=list[ComplianceRiskResponse]
)
def get_high_risk_contracts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    contracts = db.query(Contract).all()

    results = []

    for contract in contracts:

        result = calculate_contract_compliance(
            contract,
            db
        )

        if result["risk_level"] == "High":

            results.append({
                "contract_id": result["contract_id"],
                "contract_number": result["contract_number"],
                "compliance_status": result["compliance_status"],
                "compliance_score": result["compliance_score"],
                "overdue_obligations": result["overdue_obligations"],
                "risk_level": result["risk_level"]
            })

    return results