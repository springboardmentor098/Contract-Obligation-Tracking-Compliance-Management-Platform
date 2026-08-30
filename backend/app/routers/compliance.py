from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.contract import Contract
from app.models.compliance import Compliance
from app.models.user import User
from app.schemas.compliance import (
    ComplianceHistoryResponse,
    ComplianceResponse,
    ComplianceSummary,
)
from app.services.compliance_service import (
    calculate_contract_compliance,
    get_compliance_summary,
    get_contract_compliance,
)

router = APIRouter(
    prefix="/compliance",
    tags=["Compliance"],
)


# ============================================================
# Helper functions
# ============================================================

def get_contract_or_404(
    contract_id: UUID,
    db: Session,
) -> Contract:
    contract = db.get(Contract, contract_id)

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    return contract


def check_contract_access(
    contract: Contract,
    current_user: User,
) -> None:
    """
    Allow administrators, contract creators, and assigned users
    to access the contract's compliance information.
    """

    if current_user.role.lower() == "admin":
        return

    if contract.created_by == current_user.id:
        return

    if contract.assigned_to == current_user.id:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this contract",
    )


def get_user_contract_ids(
    db: Session,
    current_user: User,
):
    """
    Return a query containing the IDs of contracts accessible
    to the current user.

    Administrators can access all contracts, so None is returned
    for administrators.
    """

    if current_user.role.lower() == "admin":
        return None

    return select(Contract.id).where(
        (Contract.created_by == current_user.id)
        | (Contract.assigned_to == current_user.id)
    )


# ============================================================
# 1. Evaluate contract compliance
# ============================================================

@router.post(
    "/contracts/{contract_id}/evaluate",
    response_model=ComplianceResponse,
)
def evaluate_contract_compliance(
    contract_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contract = get_contract_or_404(
        contract_id=contract_id,
        db=db,
    )

    check_contract_access(
        contract=contract,
        current_user=current_user,
    )

    try:
        return calculate_contract_compliance(
            db=db,
            contract_id=contract_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


# ============================================================
# 2. Get latest compliance status for a contract
# ============================================================

@router.get(
    "/contracts/{contract_id}",
    response_model=ComplianceResponse,
)
def get_contract_compliance_status(
    contract_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contract = get_contract_or_404(
        contract_id=contract_id,
        db=db,
    )

    check_contract_access(
        contract=contract,
        current_user=current_user,
    )

    compliance = get_contract_compliance(
        db=db,
        contract_id=contract_id,
    )

    if compliance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Compliance record not found. "
                "Evaluate the contract first."
            ),
        )

    return compliance


# ============================================================
# 3. Compliance dashboard summary
# ============================================================

@router.get(
    "/summary",
    response_model=ComplianceSummary,
)
def get_compliance_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Administrator can see all compliance records.
    if current_user.role.lower() == "admin":
        return get_compliance_summary(db)

    # Non-admin users can only see contracts they created
    # or contracts assigned to them.
    contract_ids = get_user_contract_ids(
        db=db,
        current_user=current_user,
    )

    records = db.execute(
        select(Compliance).where(
            Compliance.contract_id.in_(contract_ids)
        )
    ).scalars().all()

    total_contracts = len(records)

    compliant_contracts = sum(
        1
        for record in records
        if record.compliance_status == "Compliant"
    )

    non_compliant_contracts = sum(
        1
        for record in records
        if record.compliance_status == "Non-Compliant"
    )

    high_risk_contracts = sum(
        1
        for record in records
        if record.risk_level == "High"
    )

    average_compliance_score = (
        round(
            sum(
                record.compliance_score
                for record in records
            )
            / total_contracts,
            2,
        )
        if total_contracts
        else 0.0
    )

    return {
        "total_contracts": total_contracts,
        "compliant_contracts": compliant_contracts,
        "non_compliant_contracts": non_compliant_contracts,
        "high_risk_contracts": high_risk_contracts,
        "average_compliance_score": average_compliance_score,
    }


# ============================================================
# 4. Get compliance history for a contract
# ============================================================

@router.get(
    "/contracts/{contract_id}/history",
    response_model=list[ComplianceHistoryResponse],
)
def get_compliance_history(
    contract_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contract = get_contract_or_404(
        contract_id=contract_id,
        db=db,
    )

    check_contract_access(
        contract=contract,
        current_user=current_user,
    )

    return db.execute(
        select(Compliance)
        .where(
            Compliance.contract_id == contract_id,
        )
        .order_by(
            Compliance.evaluated_at.desc()
        )
    ).scalars().all()


# ============================================================
# 5. Get all compliance records
# ============================================================

@router.get(
    "",
    response_model=list[ComplianceResponse],
)
def get_all_compliance_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return all compliance records accessible to the user.

    Administrator:
        Returns compliance records for all contracts.

    Other users:
        Returns records only for contracts they created
        or contracts assigned to them.
    """

    if current_user.role.lower() == "admin":
        return db.execute(
            select(Compliance)
            .order_by(
                Compliance.evaluated_at.desc()
            )
        ).scalars().all()

    contract_ids = get_user_contract_ids(
        db=db,
        current_user=current_user,
    )

    return db.execute(
        select(Compliance)
        .where(
            Compliance.contract_id.in_(contract_ids)
        )
        .order_by(
            Compliance.evaluated_at.desc()
        )
    ).scalars().all()


# ============================================================
# 6. Get non-compliant contracts
# ============================================================

@router.get(
    "/non-compliant",
    response_model=list[ComplianceResponse],
)
def get_non_compliant_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return compliance records where the compliance status
    is Non-Compliant.
    """

    if current_user.role.lower() == "admin":
        return db.execute(
            select(Compliance)
            .where(
                Compliance.compliance_status == "Non-Compliant"
            )
            .order_by(
                Compliance.evaluated_at.desc()
            )
        ).scalars().all()

    contract_ids = get_user_contract_ids(
        db=db,
        current_user=current_user,
    )

    return db.execute(
        select(Compliance)
        .where(
            Compliance.contract_id.in_(contract_ids),
            Compliance.compliance_status == "Non-Compliant",
        )
        .order_by(
            Compliance.evaluated_at.desc()
        )
    ).scalars().all()


# ============================================================
# 7. Get high-risk contracts
# ============================================================

@router.get(
    "/high-risk",
    response_model=list[ComplianceResponse],
)
def get_high_risk_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return compliance records where the risk level is High.
    """

    if current_user.role.lower() == "admin":
        return db.execute(
            select(Compliance)
            .where(
                Compliance.risk_level == "High"
            )
            .order_by(
                Compliance.evaluated_at.desc()
            )
        ).scalars().all()

    contract_ids = get_user_contract_ids(
        db=db,
        current_user=current_user,
    )

    return db.execute(
        select(Compliance)
        .where(
            Compliance.contract_id.in_(contract_ids),
            Compliance.risk_level == "High",
        )
        .order_by(
            Compliance.evaluated_at.desc()
        )
    ).scalars().all()