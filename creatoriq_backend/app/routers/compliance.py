from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.models.contract import Contract

from app.schemas.compliance import (
    ContractComplianceResponse,
    ComplianceHistoryResponse,
    ComplianceListResponse,
    ComplianceSummaryResponse,
)

from app.services.compliance_service import (
    calculate_contract_compliance,
    get_all_compliance,
    get_compliance_summary,
    get_non_compliant_contracts,
    get_high_risk_contracts,
    get_compliance_history,
)


# =========================================================
# COMPLIANCE ROUTER
# =========================================================

router = APIRouter(
    prefix="/compliance",
    tags=["Compliance"]
)


# =========================================================
# CONTRACT COMPLIANCE ROUTER
# =========================================================

contract_compliance_router = APIRouter(
    prefix="/contracts",
    tags=["Compliance"]
)


# =========================================================
# HELPER - CHECK CONTRACT ACCESS
# =========================================================

def check_contract_access(
    contract: Contract,
    current_user: User
):
    """
    Check whether the authenticated user is authorized
    to view compliance information for the contract.

    Access rules are based only on the existing
    Contract fields and existing user roles.
    """

    # Administrator has broad access
    if current_user.role == "Administrator":
        return

    # Compliance Officers can view compliance information
    if current_user.role == "Compliance Officer":
        return

    # Legal Managers can access contracts they created
    if (
        current_user.role == "Legal Manager"
        and contract.created_by == current_user.id
    ):
        return

    # Contract Managers can access contracts assigned to them
    if (
        current_user.role == "Contract Manager"
        and contract.assigned_to == current_user.id
    ):
        return

    # Employees can access contracts assigned to them
    if (
        current_user.role == "Employee"
        and contract.assigned_to == current_user.id
    ):
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not authorized to access compliance information for this contract",
    )


# =========================================================
# 1. GET CURRENT CONTRACT COMPLIANCE
# GET /contracts/{contract_id}/compliance
# =========================================================

@contract_compliance_router.get(
    "/{contract_id}/compliance",
    response_model=ContractComplianceResponse
)
def get_contract_compliance(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    check_contract_access(
        contract,
        current_user
    )

    result = calculate_contract_compliance(
        db,
        contract_id
    )

    return result


# =========================================================
# 2. GET ALL COMPLIANCE RECORDS
# GET /compliance
# =========================================================

@router.get(
    "",
    response_model=list[ComplianceListResponse]
)
def get_all_contract_compliance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_all_compliance(db)


# =========================================================
# 3. GET COMPLIANCE SUMMARY
# GET /compliance/summary
# =========================================================

@router.get(
    "/summary",
    response_model=ComplianceSummaryResponse
)
def get_compliance_summary_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_compliance_summary(db)


# =========================================================
# 4. GET NON-COMPLIANT CONTRACTS
# GET /compliance/non-compliant
# =========================================================

@router.get(
    "/non-compliant",
    response_model=list[ComplianceListResponse]
)
def get_non_compliant(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_non_compliant_contracts(db)


# =========================================================
# 5. GET HIGH-RISK CONTRACTS
# GET /compliance/high-risk
# =========================================================

@router.get(
    "/high-risk",
    response_model=list[ComplianceListResponse]
)
def get_high_risk(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_high_risk_contracts(db)


# =========================================================
# 6. GET COMPLIANCE HISTORY
# GET /compliance/contract/{contract_id}/history
# =========================================================

@router.get(
    "/contract/{contract_id}/history",
    response_model=list[ComplianceHistoryResponse]
)
def get_contract_compliance_history(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    check_contract_access(
        contract,
        current_user
    )

    return get_compliance_history(
        db,
        contract_id
    )