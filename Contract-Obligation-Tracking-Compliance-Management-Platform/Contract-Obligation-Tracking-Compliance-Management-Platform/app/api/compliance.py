from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.schemas.compliance import (
    ComplianceResponse,
    ComplianceRecordResponse,
    ComplianceSummary,
    ComplianceRiskResponse,
)
from app.services.compliance_service import (
    evaluate_contract_compliance,
    get_all_contract_compliance,
)
from app.utils.authorization import get_current_user


router = APIRouter(
    tags=["Compliance"]
)


def get_contract_or_404(
    contract_id: int,
    db: Session,
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    return contract


@router.get(
    "/contracts/{contract_id}/compliance",
    response_model=ComplianceResponse,
)
def get_contract_compliance(
    contract_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contract = get_contract_or_404(
        contract_id,
        db,
    )

    return evaluate_contract_compliance(
        contract,
        db,
    )


@router.get(
    "/compliance",
    response_model=list[ComplianceRecordResponse],
)
def get_compliance_records(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_all_contract_compliance(db)


@router.get(
    "/compliance/summary",
    response_model=ComplianceSummary,
)
def get_compliance_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = get_all_contract_compliance(db)

    return {
        "total_contracts": len(records),
        "compliant_contracts": sum(
            1 for record in records
            if record["compliance_status"] == "Compliant"
        ),
        "pending_contracts": sum(
            1 for record in records
            if record["compliance_status"] == "Pending"
        ),
        "delayed_contracts": sum(
            1 for record in records
            if record["compliance_status"] == "Delayed"
        ),
        "non_compliant_contracts": sum(
            1 for record in records
            if record["compliance_status"] == "Non-Compliant"
        ),
        "high_risk_contracts": sum(
            1 for record in records
            if record["compliance_status"] == "High Risk"
        ),
    }


@router.get(
    "/compliance/non-compliant",
    response_model=list[ComplianceRiskResponse],
)
def get_non_compliant_contracts(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = get_all_contract_compliance(db)

    return [
        {
            "contract_id": record["contract_id"],
            "contract_number": record["contract_number"],
            "risk_level": record["risk_level"],
            "overdue_obligations": record["overdue_obligations"],
        }
        for record in records
        if record["compliance_status"] == "Non-Compliant"
    ]


@router.get(
    "/compliance/high-risk",
    response_model=list[ComplianceRiskResponse],
)
def get_high_risk_contracts(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = get_all_contract_compliance(db)

    return [
        {
            "contract_id": record["contract_id"],
            "contract_number": record["contract_number"],
            "risk_level": record["risk_level"],
            "overdue_obligations": record["overdue_obligations"],
        }
        for record in records
        if record["risk_level"] == "High"
    ]
