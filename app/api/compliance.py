from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.contract import Contract
from app.models.user import User
from app.schemas.compliance import (
    ComplianceHistoryResponse,
    ComplianceListItemResponse,
    ComplianceSummaryResponse,
    ContractComplianceResponse,
    HighRiskContractResponse,
    NonCompliantContractResponse,
)
from app.services import compliance_service

router = APIRouter(
    tags=["Compliance"]
)


@router.get(
    "/contracts/{contract_id}/compliance",
    response_model=ContractComplianceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Contract Compliance Status",
    description="Evaluates obligations and returns compliance status, score, and risk level for a specific contract."
)
def get_contract_compliance(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve compliance evaluation for a single contract."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found."
        )

    record = compliance_service.evaluate_contract_compliance(contract_id, db)

    return ContractComplianceResponse(
        contract_id=contract.id,
        contract_number=contract.contract_number,
        title=contract.title,
        compliance_status=record.compliance_status,
        compliance_score=record.compliance_score,
        risk_level=record.risk_level,
        total_obligations=record.total_obligations,
        completed_obligations=record.completed_obligations,
        pending_obligations=record.pending_obligations,
        overdue_obligations=record.overdue_obligations,
        delayed_obligations=record.delayed_obligations,
        evaluated_at=record.evaluated_at,
        notes=record.notes
    )


@router.get(
    "/contracts/{contract_id}/compliance/history",
    response_model=List[ComplianceHistoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Contract Compliance Audit History",
    description="Retrieves full historical timeline of compliance evaluations for audit and reporting."
)
def get_contract_compliance_history(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve evaluation audit history for a contract."""
    history = compliance_service.get_contract_compliance_history(contract_id, db)
    return history


@router.get(
    "/compliance",
    response_model=List[ComplianceListItemResponse],
    status_code=status.HTTP_200_OK,
    summary="Get All Compliance Records",
    description="Retrieves current compliance evaluation records for all contracts authorized to view."
)
def get_all_compliance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve compliance records for all contracts."""
    records = compliance_service.get_all_compliance_records(db)
    return records


@router.get(
    "/compliance/summary",
    response_model=ComplianceSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Compliance Summary",
    description="Provides overall compliance dashboard metrics across all contracts."
)
def get_compliance_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve compliance summary statistics."""
    summary = compliance_service.get_compliance_summary(db)
    return summary


@router.get(
    "/compliance/non-compliant",
    response_model=List[NonCompliantContractResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Non-Compliant Contracts",
    description="Identifies all contracts that have missed obligations or non-compliant status."
)
def get_non_compliant_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve contracts with compliance issues."""
    non_compliant = compliance_service.get_non_compliant_contracts(db)
    return non_compliant


@router.get(
    "/compliance/high-risk",
    response_model=List[HighRiskContractResponse],
    status_code=status.HTTP_200_OK,
    summary="Get High-Risk Contracts",
    description="Identifies contracts requiring immediate attention due to high compliance risk."
)
def get_high_risk_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve high-risk contracts."""
    high_risk = compliance_service.get_high_risk_contracts(db)
    return high_risk
