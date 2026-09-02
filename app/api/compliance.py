from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.services.compliance_service import (
    calculate_contract_compliance,
    calculate_all_contract_compliance,
    calculate_compliance_summary,
    get_non_compliant_contracts,
    get_high_risk_contracts,
    get_compliance_history,
)

from app.schemas.compliance_schema import (
    ComplianceResponse,
    ComplianceSummaryResponse,
    ComplianceHistoryResponse,
)

from app.middleware.auth import get_current_user


# ============================================================
# COMPLIANCE ROUTER
# ============================================================

router = APIRouter(
    prefix="/compliance",
    tags=["Compliance"]
)


# ============================================================
# GET COMPLIANCE FOR ONE CONTRACT
# ============================================================

@router.get(
    "/contract/{contract_id}",
    response_model=ComplianceResponse
)
def get_contract_compliance(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = calculate_contract_compliance(
        db=db,
        contract_id=contract_id
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return result


# ============================================================
# GET ALL CONTRACT COMPLIANCE
# ============================================================

@router.get(
    "/",
    response_model=list[ComplianceResponse]
)
def get_all_compliance(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return calculate_all_contract_compliance(db)


# ============================================================
# GET COMPLIANCE SUMMARY
# ============================================================

@router.get(
    "/summary",
    response_model=ComplianceSummaryResponse
)
def get_compliance_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return calculate_compliance_summary(db)


# ============================================================
# GET NON-COMPLIANT CONTRACTS
# ============================================================

@router.get(
    "/non-compliant",
    response_model=list[ComplianceResponse]
)
def get_non_compliant(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return get_non_compliant_contracts(db)


# ============================================================
# GET HIGH-RISK CONTRACTS
# ============================================================

@router.get(
    "/high-risk",
    response_model=list[ComplianceResponse]
)
def get_high_risk(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return get_high_risk_contracts(db)


# ============================================================
# GET COMPLIANCE HISTORY
# ============================================================

@router.get(
    "/contract/{contract_id}/history",
    response_model=list[ComplianceHistoryResponse]
)
def get_contract_compliance_history(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    history = get_compliance_history(
        db=db,
        contract_id=contract_id
    )

    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return history