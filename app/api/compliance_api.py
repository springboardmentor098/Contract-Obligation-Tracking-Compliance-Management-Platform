from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.schemas.compliance_schema import (
    ComplianceResponse,
    ComplianceSummaryResponse
)
from app.services.compliance_service import calculate_compliance
from app.core.auth import get_current_user

router = APIRouter(
    prefix="/compliance",
    tags=["Compliance"]
)


# ---------------- CONTRACT COMPLIANCE ----------------

@router.get(
    "/contracts/{contract_id}",
    response_model=ComplianceResponse
)
def get_contract_compliance(
    contract_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found"
        )

    result = calculate_compliance(contract)

    return {
        "contract_id": contract.id,
        "contract_title": contract.title,
        **result
    }


# ---------------- ALL CONTRACTS ----------------

@router.get(
    "",
    response_model=list[ComplianceResponse]
)
def get_all_compliance(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contracts = db.query(Contract).all()

    response = []

    for contract in contracts:
        result = calculate_compliance(contract)

        response.append({
            "contract_id": contract.id,
            "contract_title": contract.title,
            **result
        })

    return response


# ---------------- SUMMARY ----------------

@router.get(
    "/summary",
    response_model=ComplianceSummaryResponse
)
def compliance_summary(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contracts = db.query(Contract).all()

    compliant = 0
    partial = 0
    non = 0

    for contract in contracts:
        result = calculate_compliance(contract)

        if result["status"] == "Compliant":
            compliant += 1
        elif result["status"] == "Partially Compliant":
            partial += 1
        else:
            non += 1

    return {
        "total_contracts": len(contracts),
        "compliant": compliant,
        "partially_compliant": partial,
        "non_compliant": non
    }


# ---------------- HIGH RISK ----------------

@router.get(
    "/high-risk",
    response_model=list[ComplianceResponse]
)
def high_risk_contracts(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contracts = db.query(Contract).all()

    response = []

    for contract in contracts:
        result = calculate_compliance(contract)

        if result["risk_level"] == "High":
            response.append({
                "contract_id": contract.id,
                "contract_title": contract.title,
                **result
            })

    return response


# ---------------- NON COMPLIANT ----------------

@router.get(
    "/non-compliant",
    response_model=list[ComplianceResponse]
)
def non_compliant_contracts(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contracts = db.query(Contract).all()

    response = []

    for contract in contracts:
        result = calculate_compliance(contract)

        if result["status"] == "Non-Compliant":
            response.append({
                "contract_id": contract.id,
                "contract_title": contract.title,
                **result
            })

    return response