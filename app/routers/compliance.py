from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.contract import Contract
from app.schemas.compliance import (
    ComplianceResponse,
    ComplianceSummary,
    RiskInformation
)
from app.services.compliance_service import (
    calculate_compliance,
    get_all_compliance,
    get_compliance_summary,
    get_non_compliant_contracts,
    get_high_risk_contracts
)


router = APIRouter(
    tags=["Compliance"]
)


# =========================
# GET CONTRACT COMPLIANCE
# =========================

@router.get(
    "/contracts/{contract_id}/compliance",
    response_model=ComplianceResponse,
    status_code=status.HTTP_200_OK
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

    return calculate_compliance(
        contract,
        db
    )


# =========================
# GET ALL COMPLIANCE
# =========================

@router.get(
    "/compliance",
    status_code=status.HTTP_200_OK
)
def get_compliance(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return get_all_compliance(db)


# =========================
# GET COMPLIANCE SUMMARY
# =========================

@router.get(
    "/compliance/summary",
    response_model=ComplianceSummary,
    status_code=status.HTTP_200_OK
)
def compliance_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return get_compliance_summary(db)


# =========================
# GET NON-COMPLIANT CONTRACTS
# =========================

@router.get(
    "/compliance/non-compliant",
    status_code=status.HTTP_200_OK
)
def non_compliant_contracts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return get_non_compliant_contracts(db)


# =========================
# GET HIGH-RISK CONTRACTS
# =========================

@router.get(
    "/compliance/high-risk",
    response_model=list[RiskInformation],
    status_code=status.HTTP_200_OK
)
def high_risk_contracts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return get_high_risk_contracts(db)