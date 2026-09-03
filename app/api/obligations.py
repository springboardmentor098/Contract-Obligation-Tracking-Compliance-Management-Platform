from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.contract import Contract
from app.models.obligation import Obligation, ObligationStatus, OBLIGATION_STATUS_TRANSITIONS
from app.schemas.obligation import (
    ObligationCreate,
    ObligationUpdate,
    ObligationStatusUpdate,
    ObligationResponse,
    ObligationListItem,
)
from app.core.deps import get_current_active_user
from app.services.notification_service import notify_obligation_overdue

router = APIRouter(tags=["Obligations"])


def _get_obligation_or_404(db: Session, obligation_id: int) -> Obligation:
    obligation = db.query(Obligation).filter(Obligation.id == obligation_id).first()
    if not obligation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Obligation not found")
    return obligation


def _assert_transition_allowed(current: ObligationStatus, target: ObligationStatus) -> None:
    allowed = OBLIGATION_STATUS_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition obligation from {current.value} to {target.value}",
        )


def _refresh_overdue_status(db: Session, obligation: Obligation) -> None:
    """Flip Pending/In Progress/Delayed obligations to Overdue once due_date has passed."""
    if obligation.status in (ObligationStatus.COMPLETED, ObligationStatus.OVERDUE):
        return
    if obligation.due_date < date.today():
        obligation.status = ObligationStatus.OVERDUE
        db.commit()
        db.refresh(obligation)
        notify_obligation_overdue(db, obligation)


@router.post("/obligations", response_model=ObligationResponse, status_code=status.HTTP_201_CREATED)
def create_obligation(
    payload: ObligationCreate,
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

    obligation = Obligation(
        contract_id=payload.contract_id,
        title=payload.title,
        description=payload.description,
        obligation_type=payload.obligation_type,
        due_date=payload.due_date,
        assigned_to=payload.assigned_to,
        status=ObligationStatus.PENDING,
    )
    db.add(obligation)
    db.commit()
    db.refresh(obligation)
    return obligation


@router.get("/obligations", response_model=List[ObligationListItem])
def list_obligations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    obligations = db.query(Obligation).order_by(Obligation.due_date.asc()).all()
    for o in obligations:
        _refresh_overdue_status(db, o)
    return obligations


@router.get("/obligations/{obligation_id}", response_model=ObligationResponse)
def get_obligation(
    obligation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    obligation = _get_obligation_or_404(db, obligation_id)
    _refresh_overdue_status(db, obligation)
    return obligation


@router.get("/contracts/{contract_id}/obligations", response_model=List[ObligationListItem])
def get_contract_obligations(
    contract_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    obligations = (
        db.query(Obligation).filter(Obligation.contract_id == contract_id).order_by(Obligation.due_date.asc()).all()
    )
    for o in obligations:
        _refresh_overdue_status(db, o)
    return obligations


@router.put("/obligations/{obligation_id}", response_model=ObligationResponse)
def update_obligation(
    obligation_id: int,
    payload: ObligationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    obligation = _get_obligation_or_404(db, obligation_id)

    if payload.assigned_to is not None:
        assignee = db.query(User).filter(User.id == payload.assigned_to).first()
        if not assignee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned user not found")

    # completion_date and status are system-managed here, not via this endpoint.
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obligation, field, value)

    db.commit()
    db.refresh(obligation)
    return obligation


@router.patch("/obligations/{obligation_id}/status", response_model=ObligationResponse)
def update_obligation_status(
    obligation_id: int,
    payload: ObligationStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    obligation = _get_obligation_or_404(db, obligation_id)
    _assert_transition_allowed(obligation.status, payload.status)
    obligation.status = payload.status
    if payload.status == ObligationStatus.COMPLETED:
        obligation.completion_date = date.today()
    db.commit()
    db.refresh(obligation)
    return obligation


@router.post("/obligations/{obligation_id}/complete", response_model=ObligationResponse)
def complete_obligation(
    obligation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    obligation = _get_obligation_or_404(db, obligation_id)
    _assert_transition_allowed(obligation.status, ObligationStatus.COMPLETED)
    obligation.status = ObligationStatus.COMPLETED
    obligation.completion_date = date.today()  # backend-determined, never client-supplied
    db.commit()
    db.refresh(obligation)
    return obligation
