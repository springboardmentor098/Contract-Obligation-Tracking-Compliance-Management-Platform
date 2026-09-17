from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.contract_compliance import ContractCompliance

from app.schemas.contract_compliance import (
    ComplianceEvaluationCreate,
    ComplianceEvaluationResponse
)

from app.services.compliance_service import (
    calculate_compliance,
    save_compliance_record
)


router = APIRouter(
    prefix="/compliance",
    tags=["Compliance Evaluation"]
)


@router.get("/")
def get_all_compliance(
    db: Session = Depends(get_db)
):
    """
    Calculate current compliance for all contracts.
    """

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

        compliance = calculate_compliance(obligations)

        results.append({
            "contract_id": contract.id,
            **compliance,
            "evaluated_at": datetime.utcnow()
        })

    return results


@router.get(
    "/contract/{contract_id}"
)
def evaluate_contract_compliance(
    contract_id: int,
    db: Session = Depends(get_db)
):
    """
    Calculate current compliance for one contract.
    """

    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id
        )
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    obligations = (
        db.query(Obligation)
        .filter(
            Obligation.contract_id == contract_id
        )
        .all()
    )

    compliance = calculate_compliance(
        obligations
    )

    return {
        "contract_id": contract_id,
        **compliance,
        "evaluated_at": datetime.utcnow()
    }


@router.post(
    "/evaluate/{contract_id}",
    response_model=ComplianceEvaluationResponse
)
def create_compliance_evaluation(
    contract_id: int,
    evaluation: ComplianceEvaluationCreate,
    db: Session = Depends(get_db)
):
    """
    Calculate and save a compliance evaluation
    for a contract.
    """

    # Make sure the URL contract_id
    # matches the request body.
    if evaluation.contract_id != contract_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract ID in URL and request body must match"
        )

    # Check contract
    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id
        )
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Get obligations
    obligations = (
        db.query(Obligation)
        .filter(
            Obligation.contract_id == contract_id
        )
        .all()
    )

    # Calculate compliance
    compliance = calculate_compliance(
        obligations
    )

    # Save result
    record = save_compliance_record(
        db=db,
        contract_id=contract_id,
        compliance_result=compliance,
        notes=evaluation.notes
    )

    return record


@router.get(
    "/records",
    response_model=list[ComplianceEvaluationResponse]
)
def get_saved_compliance_records(
    db: Session = Depends(get_db)
):
    """
    Get all saved compliance evaluations.
    """

    records = (
        db.query(ContractCompliance)
        .order_by(
            ContractCompliance.evaluated_at.desc()
        )
        .all()
    )

    return records


@router.get(
    "/records/{record_id}",
    response_model=ComplianceEvaluationResponse
)
def get_compliance_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    Get one saved compliance evaluation.
    """

    record = (
        db.query(ContractCompliance)
        .filter(
            ContractCompliance.id == record_id
        )
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance record not found"
        )

    return record


@router.get(
    "/contract/{contract_id}/history",
    response_model=list[ComplianceEvaluationResponse]
)
def get_contract_compliance_history(
    contract_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all saved compliance evaluations
    for a specific contract.
    """

    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id
        )
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    records = (
        db.query(ContractCompliance)
        .filter(
            ContractCompliance.contract_id == contract_id
        )
        .order_by(
            ContractCompliance.evaluated_at.desc()
        )
        .all()
    )

    return records