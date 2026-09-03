from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.models.contract import Contract, ContractStatus, CONTRACT_STATUS_TRANSITIONS
from app.schemas.contract import (
    ContractCreate,
    ContractUpdate,
    ContractStatusUpdate,
    ContractAssignmentUpdate,
    ContractResponse,
    ContractListItem,
)
from app.core.deps import get_current_active_user
from app.core.permissions import require_roles, APPROVAL_ROLES, COMPLIANCE_VIEW_ROLES
from app.services.notification_service import (
    notify_contract_submitted_for_review,
    notify_contract_approved,
    notify_contract_status_change,
)
from app.services.compliance_service import evaluate_contract_compliance, record_compliance_evaluation
from app.schemas.compliance import ContractComplianceResponse

router = APIRouter(prefix="/contracts", tags=["Contracts"])


def _get_contract_or_404(db: Session, contract_id: int) -> Contract:
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return contract


def _assert_transition_allowed(current: ContractStatus, target: ContractStatus) -> None:
    allowed = CONTRACT_STATUS_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition contract from {current.value} to {target.value}",
        )


# ---------------------------------------------------------------- Sprint 7 --

@router.post("", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
def create_contract(
    payload: ContractCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    contract = Contract(
        title=payload.title,
        contract_number=payload.contract_number,
        category=payload.category,
        description=payload.description,
        start_date=payload.start_date,
        end_date=payload.end_date,
        status=ContractStatus.DRAFT,
        created_by=current_user.id,  # never trust a client-supplied created_by
    )
    db.add(contract)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A contract with this contract_number already exists",
        )
    db.refresh(contract)
    return contract


@router.get("", response_model=List[ContractListItem])
def list_contracts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Administrators/Legal Managers see everything; other roles see contracts
    # they created or are assigned to.
    query = db.query(Contract)
    if current_user.role not in (UserRole.ADMINISTRATOR, UserRole.LEGAL_MANAGER):
        query = query.filter(
            (Contract.created_by == current_user.id) | (Contract.assigned_to == current_user.id)
        )
    return query.order_by(Contract.created_at.desc()).all()


@router.get("/{contract_id}", response_model=ContractResponse)
def get_contract(
    contract_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return _get_contract_or_404(db, contract_id)


# ---------------------------------------------------------------- Sprint 8 --

@router.put("/{contract_id}", response_model=ContractResponse)
def update_contract(
    contract_id: int,
    payload: ContractUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    contract = _get_contract_or_404(db, contract_id)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(contract, field, value)

    db.commit()
    db.refresh(contract)
    return contract


@router.patch("/{contract_id}/status", response_model=ContractResponse)
def update_contract_status(
    contract_id: int,
    payload: ContractStatusUpdate,
    current_user: User = Depends(require_roles(*APPROVAL_ROLES, UserRole.CONTRACT_MANAGER)),
    db: Session = Depends(get_db),
):
    contract = _get_contract_or_404(db, contract_id)
    _assert_transition_allowed(contract.status, payload.status)
    contract.status = payload.status
    db.commit()
    db.refresh(contract)
    notify_contract_status_change(db, contract, contract.created_by)
    return contract


@router.post("/{contract_id}/submit-review", response_model=ContractResponse)
def submit_for_review(
    contract_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    contract = _get_contract_or_404(db, contract_id)
    _assert_transition_allowed(contract.status, ContractStatus.UNDER_REVIEW)
    contract.status = ContractStatus.UNDER_REVIEW
    contract.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(contract)

    legal_managers = [u.id for u in db.query(User).filter(User.role == UserRole.LEGAL_MANAGER).all()]
    notify_contract_submitted_for_review(db, contract, legal_managers)
    return contract


@router.post("/{contract_id}/approve", response_model=ContractResponse)
def approve_contract(
    contract_id: int,
    current_user: User = Depends(require_roles(*APPROVAL_ROLES)),
    db: Session = Depends(get_db),
):
    contract = _get_contract_or_404(db, contract_id)
    _assert_transition_allowed(contract.status, ContractStatus.APPROVED)
    contract.status = ContractStatus.APPROVED
    contract.approved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(contract)
    notify_contract_approved(db, contract, contract.created_by)
    return contract


@router.post("/{contract_id}/activate", response_model=ContractResponse)
def activate_contract(
    contract_id: int,
    current_user: User = Depends(require_roles(*APPROVAL_ROLES, UserRole.CONTRACT_MANAGER)),
    db: Session = Depends(get_db),
):
    contract = _get_contract_or_404(db, contract_id)
    _assert_transition_allowed(contract.status, ContractStatus.ACTIVE)
    contract.status = ContractStatus.ACTIVE
    contract.activated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(contract)
    notify_contract_status_change(db, contract, contract.created_by)
    return contract


@router.patch("/{contract_id}/assign", response_model=ContractResponse)
def assign_contract(
    contract_id: int,
    payload: ContractAssignmentUpdate,
    current_user: User = Depends(require_roles(*APPROVAL_ROLES)),
    db: Session = Depends(get_db),
):
    contract = _get_contract_or_404(db, contract_id)
    assignee = db.query(User).filter(User.id == payload.assigned_to).first()
    if not assignee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned user not found")
    contract.assigned_to = payload.assigned_to
    db.commit()
    db.refresh(contract)
    return contract


# ---------------------------------------------------------------- Sprint 11 --

@router.get("/{contract_id}/compliance", response_model=ContractComplianceResponse)
def get_contract_compliance(
    contract_id: int,
    current_user: User = Depends(require_roles(*COMPLIANCE_VIEW_ROLES)),
    db: Session = Depends(get_db),
):
    contract = _get_contract_or_404(db, contract_id)
    result = evaluate_contract_compliance(db, contract)
    record = record_compliance_evaluation(db, contract, result)

    return ContractComplianceResponse(
        contract_id=contract.id,
        contract_number=contract.contract_number,
        compliance_status=result.compliance_status,
        compliance_score=result.compliance_score,
        total_obligations=result.total_obligations,
        completed_obligations=result.completed_obligations,
        pending_obligations=result.pending_obligations,
        in_progress_obligations=result.in_progress_obligations,
        delayed_obligations=result.delayed_obligations,
        overdue_obligations=result.overdue_obligations,
        risk_level=result.risk_level,
        evaluated_at=record.evaluated_at,
    )
