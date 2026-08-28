from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.compliance import (
    ComplianceResponse,
    ComplianceSummary,
    ComplianceContractResponse,
)

from app.services.compliance import (
    calculate_contract_compliance,
    get_all_compliance,
    get_compliance_summary,
    get_non_compliant_contracts,
    get_high_risk_contracts,
)


router = APIRouter(
    prefix="/compliance",
    tags=["Compliance"]
)


# GET CONTRACT COMPLIANCE
@router.get(
    "/contract/{contract_id}",
    response_model=ComplianceResponse
)
def get_contract_compliance_api(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = calculate_contract_compliance(
        db,
        contract_id
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return result


# GET ALL COMPLIANCE
@router.get(
    "",
    response_model=list[ComplianceContractResponse]
)
def get_all_compliance_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_all_compliance(db)


# GET COMPLIANCE SUMMARY
@router.get(
    "/summary",
    response_model=ComplianceSummary
)
def get_compliance_summary_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_compliance_summary(db)


# GET NON-COMPLIANT CONTRACTS
@router.get(
    "/non-compliant",
    response_model=list[ComplianceContractResponse]
)
def get_non_compliant_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_non_compliant_contracts(db)


# GET HIGH-RISK CONTRACTS
@router.get(
    "/high-risk",
    response_model=list[ComplianceContractResponse]
)
def get_high_risk_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_high_risk_contracts(db)
