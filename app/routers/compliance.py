from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.user import User
from app.schemas.compliance import ComplianceResponse
from app.services.compliance_service import calculate_contract_compliance
from app.routers.dependencies import get_current_user


router = APIRouter(
    prefix="/compliance",
    tags=["Compliance"]
)


# ============================================================
# GET COMPLIANCE FOR A CONTRACT
# ============================================================
@router.get(
    "/contracts/{contract_id}",
    response_model=ComplianceResponse
)
def get_contract_compliance(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return calculate_contract_compliance(
        db,
        contract_id
    )
# ============================================================
# GET COMPLIANCE FOR ALL CONTRACTS
# ============================================================
@router.get(
    "",
    response_model=list[ComplianceResponse]
)
def get_all_compliance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contracts = db.query(Contract).all()

    compliance_results = []

    for contract in contracts:
        result = calculate_contract_compliance(
            db,
            contract.id
        )

        compliance_results.append(result)

    return compliance_results
# ============================================================
# GET NON-COMPLIANT CONTRACTS
# ============================================================
@router.get(
    "/non-compliant",
    response_model=list[ComplianceResponse]
)
def get_non_compliant_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contracts = db.query(Contract).all()

    non_compliant = []

    for contract in contracts:
        result = calculate_contract_compliance(
            db,
            contract.id
        )

        if result["compliance_status"] == "Non-Compliant":
            non_compliant.append(result)

    return non_compliant
# ============================================================
# GET HIGH-RISK CONTRACTS
# ============================================================
@router.get(
    "/high-risk",
    response_model=list[ComplianceResponse]
)
def get_high_risk_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contracts = db.query(Contract).all()

    high_risk = []

    for contract in contracts:
        result = calculate_contract_compliance(
            db,
            contract.id
        )

        if result["risk_level"] == "High":
            high_risk.append(result)

    return high_risk

# ============================================================
# GET COMPLIANCE SUMMARY
# ============================================================
@router.get(
    "/summary"
)
def get_compliance_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contracts = db.query(Contract).all()

    total_contracts = len(contracts)

    compliant = 0
    partially_compliant = 0
    non_compliant = 0
    high_risk = 0

    for contract in contracts:
        result = calculate_contract_compliance(
            db,
            contract.id
        )

        if result["compliance_status"] == "Compliant":
            compliant += 1

        elif result["compliance_status"] == "Partially Compliant":
            partially_compliant += 1

        elif result["compliance_status"] == "Non-Compliant":
            non_compliant += 1

        if result["risk_level"] == "High":
            high_risk += 1

    return {
        "total_contracts": total_contracts,
        "compliant_contracts": compliant,
        "partially_compliant_contracts": partially_compliant,
        "non_compliant_contracts": non_compliant,
        "high_risk_contracts": high_risk
    }