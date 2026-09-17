from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.compliance import ComplianceRecord
from app.models.user import User
from app.services.compliance_service import calculate_contract_compliance
from app.schemas.compliance import (
    ComplianceResponse,
    ComplianceListResponse,
    ComplianceSummaryResponse
)

# Use the same authentication import you already use in your other protected routers
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/compliance",
    tags=["Compliance"]
)


def get_compliance_data(contract, db):
    obligations = (
        db.query(Obligation)
        .filter(Obligation.contract_id == contract.id)
        .all()
    )

    compliance_data = calculate_contract_compliance(obligations)

    return {
        "contract_id": contract.id,
        "contract_number": contract.contract_number,
        **compliance_data
    }


@router.get(
    "",
    response_model=list[ComplianceListResponse]
)
def get_all_compliance_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contracts = db.query(Contract).all()

    return [
        get_compliance_data(contract, db)
        for contract in contracts
    ]


@router.get(
    "/summary",
    response_model=ComplianceSummaryResponse
)
def get_compliance_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contracts = db.query(Contract).all()

    summary = {
        "total_contracts": len(contracts),
        "compliant_contracts": 0,
        "pending_contracts": 0,
        "delayed_contracts": 0,
        "non_compliant_contracts": 0,
        "high_risk_contracts": 0
    }

    for contract in contracts:
        data = get_compliance_data(contract, db)

        if data["compliance_status"] == "Compliant":
            summary["compliant_contracts"] += 1

        elif data["compliance_status"] == "Pending":
            summary["pending_contracts"] += 1

        elif data["compliance_status"] == "Delayed":
            summary["delayed_contracts"] += 1

        elif data["compliance_status"] == "Non-Compliant":
            summary["non_compliant_contracts"] += 1

        elif data["compliance_status"] == "High Risk":
            summary["high_risk_contracts"] += 1

    return summary


@router.get(
    "/non-compliant",
    response_model=list[ComplianceListResponse]
)
def get_non_compliant_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contracts = db.query(Contract).all()

    results = []

    for contract in contracts:
        data = get_compliance_data(contract, db)

        if data["compliance_status"] in [
            "Non-Compliant",
            "High Risk"
        ]:
            results.append(data)

    return results


@router.get(
    "/high-risk",
    response_model=list[ComplianceListResponse]
)
def get_high_risk_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contracts = db.query(Contract).all()

    results = []

    for contract in contracts:
        data = get_compliance_data(contract, db)

        if data["risk_level"] == "High":
            results.append(data)

    return results
@router.get(
    "/{contract_id}/history"
)
def get_compliance_history(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    history = (
        db.query(ComplianceRecord)
        .filter(ComplianceRecord.contract_id == contract_id)
        .order_by(ComplianceRecord.evaluated_at.desc())
        .all()
    )

    return history