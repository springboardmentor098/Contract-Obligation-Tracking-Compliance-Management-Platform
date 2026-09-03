from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.contract import Contract, ContractStatus
from app.models.renewal import Renewal, RenewalStatus, RENEWAL_STATUS_TRANSITIONS
from app.schemas.renewal import (
    RenewalCreate,
    RenewalUpdate,
    RenewalStatusUpdate,
    RenewalResponse,
)
from app.core.deps import get_current_active_user

router = APIRouter(tags=["Renewals"])


def _get_renewal_or_404(db: Session, renewal_id: int) -> Renewal:
    renewal = db.query(Renewal).filter(Renewal.id == renewal_id).first()
    if not renewal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Renewal not found")
    return renewal


def _assert_transition_allowed(current: RenewalStatus, target: RenewalStatus) -> None:
    allowed = RENEWAL_STATUS_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition renewal from {current.value} to {target.value}",
        )


@router.post("/renewals", response_model=RenewalResponse, status_code=status.HTTP_201_CREATED)
def create_renewal(
    payload: RenewalCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    contract = db.query(Contract).filter(Contract.id == payload.contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    if payload.assigned_to is not None:
        assignee = db.query(User).filter(User.id == payload.assigned_to).first()
        if not assignee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned user not found")

    renewal = Renewal(
        contract_id=payload.contract_id,
        renewal_date=payload.renewal_date,
        previous_expiry_date=payload.previous_expiry_date,
        new_expiry_date=payload.new_expiry_date,
        assigned_to=payload.assigned_to,
        notes=payload.notes,
        status=RenewalStatus.UPCOMING,
    )
    db.add(renewal)
    db.commit()
    db.refresh(renewal)
    return renewal


@router.get("/renewals", response_model=List[RenewalResponse])
def list_renewals(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return db.query(Renewal).order_by(Renewal.renewal_date.asc()).all()


@router.get("/renewals/{renewal_id}", response_model=RenewalResponse)
def get_renewal(
    renewal_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return _get_renewal_or_404(db, renewal_id)


@router.get("/contracts/{contract_id}/renewals", response_model=List[RenewalResponse])
def get_contract_renewals(
    contract_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return (
        db.query(Renewal)
        .filter(Renewal.contract_id == contract_id)
        .order_by(Renewal.renewal_date.desc())
        .all()
    )


@router.put("/renewals/{renewal_id}", response_model=RenewalResponse)
def update_renewal(
    renewal_id: int,
    payload: RenewalUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    renewal = _get_renewal_or_404(db, renewal_id)

    if payload.assigned_to is not None:
        assignee = db.query(User).filter(User.id == payload.assigned_to).first()
        if not assignee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned user not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(renewal, field, value)

    db.commit()
    db.refresh(renewal)
    return renewal


@router.patch("/renewals/{renewal_id}/status", response_model=RenewalResponse)
def update_renewal_status(
    renewal_id: int,
    payload: RenewalStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    renewal = _get_renewal_or_404(db, renewal_id)
    _assert_transition_allowed(renewal.status, payload.status)
    renewal.status = payload.status
    db.commit()
    db.refresh(renewal)
    return renewal


@router.post("/renewals/{renewal_id}/renew", response_model=RenewalResponse)
def complete_renewal(
    renewal_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    renewal = _get_renewal_or_404(db, renewal_id)
    _assert_transition_allowed(renewal.status, RenewalStatus.RENEWED)
    renewal.status = RenewalStatus.RENEWED
    db.commit()

    # Propagate the new expiry date to the associated contract and reactivate it.
    contract = db.query(Contract).filter(Contract.id == renewal.contract_id).first()
    if contract:
        contract.end_date = renewal.new_expiry_date
        if contract.status in (ContractStatus.ACTIVE, ContractStatus.EXPIRED):
            contract.status = ContractStatus.ACTIVE
        db.commit()

    db.refresh(renewal)
    return renewal
