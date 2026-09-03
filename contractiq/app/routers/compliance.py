# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session

# from app.database.database import get_db
# from app.models.contract import Contract
# from app.models.user import User
# from app.schemas.compliance import ComplianceResponse
# from app.core.dependencies import get_current_user
# from app.services.compliance_service import calculate_contract_compliance


# router = APIRouter(
#     prefix="/compliance",
#     tags=["Compliance"]
# )


# @router.get(
#     "/contracts/{contract_id}",
#     response_model=ComplianceResponse
# )
# def get_contract_compliance(
#     contract_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     contract = (
#         db.query(Contract)
#         .filter(Contract.id == contract_id)
#         .first()
#     )

#     if contract is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Contract not found"
#         )

#     # Check whether the user can access this contract
#     if (
#         contract.owner_id != current_user.id
#         and contract.assigned_to != current_user.id
#     ):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="You do not have permission to view this contract's compliance"
#         )

#     compliance = calculate_contract_compliance(
#         contract_id,
#         db
#     )

#     return {
#         "contract_id": contract_id,
#         **compliance
#     }


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.user import User
from app.schemas.compliance import (
    ComplianceListResponse,
    ComplianceSummary,
    NonCompliantResponse,
    HighRiskResponse,
)
from app.core.dependencies import get_current_user
from app.services.compliance_service import calculate_contract_compliance


router = APIRouter(
    prefix="/compliance",
    tags=["Compliance"]
)


def get_accessible_contracts(
    current_user: User,
    db: Session
):
    return (
        db.query(Contract)
        .filter(
            (Contract.owner_id == current_user.id)
            | (Contract.assigned_to == current_user.id)
        )
        .all()
    )


@router.get(
    "/",
    response_model=list[ComplianceListResponse]
)
def get_all_compliance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contracts = get_accessible_contracts(
        current_user,
        db
    )

    results = []

    for contract in contracts:
        compliance = calculate_contract_compliance(
            contract.id,
            db
        )

        results.append({
            "contract_id": contract.id,
            "contract_number": contract.contract_code,
            "compliance_status": compliance["compliance_status"],
            "compliance_score": compliance["compliance_score"]
        })

    return results


@router.get(
    "/summary",
    response_model=ComplianceSummary
)
def get_compliance_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contracts = get_accessible_contracts(
        current_user,
        db
    )

    total_contracts = len(contracts)
    compliant_contracts = 0
    pending_contracts = 0
    delayed_contracts = 0
    non_compliant_contracts = 0
    high_risk_contracts = 0

    for contract in contracts:
        compliance = calculate_contract_compliance(
            contract.id,
            db
        )

        compliance_status = compliance["compliance_status"]

        if compliance_status == "Compliant":
            compliant_contracts += 1

        elif compliance_status == "Pending":
            pending_contracts += 1

        elif compliance_status == "Delayed":
            delayed_contracts += 1

        elif compliance_status == "Non-Compliant":
            non_compliant_contracts += 1

        elif compliance_status == "High Risk":
            high_risk_contracts += 1

    return {
        "total_contracts": total_contracts,
        "compliant_contracts": compliant_contracts,
        "pending_contracts": pending_contracts,
        "delayed_contracts": delayed_contracts,
        "non_compliant_contracts": non_compliant_contracts,
        "high_risk_contracts": high_risk_contracts
    }


@router.get(
    "/non-compliant",
    response_model=list[NonCompliantResponse]
)
def get_non_compliant_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contracts = get_accessible_contracts(
        current_user,
        db
    )

    results = []

    for contract in contracts:
        compliance = calculate_contract_compliance(
            contract.id,
            db
        )

        if compliance["compliance_status"] == "Non-Compliant":
            results.append({
                "contract_id": contract.id,
                "contract_number": contract.contract_code,
                "compliance_status": compliance["compliance_status"],
                "overdue_obligations": compliance["overdue_obligations"]
            })

    return results


@router.get(
    "/high-risk",
    response_model=list[HighRiskResponse]
)
def get_high_risk_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contracts = get_accessible_contracts(
        current_user,
        db
    )

    results = []

    for contract in contracts:
        compliance = calculate_contract_compliance(
            contract.id,
            db
        )

        if compliance["risk_level"] == "High":
            results.append({
                "contract_id": contract.id,
                "contract_number": contract.contract_code,
                "risk_level": compliance["risk_level"],
                "overdue_obligations": compliance["overdue_obligations"]
            })

    return results