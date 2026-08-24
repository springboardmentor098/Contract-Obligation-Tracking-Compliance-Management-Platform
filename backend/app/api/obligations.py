from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.obligation import Obligation
from backend.app.models.contract import Contract
from backend.app.models.user import User
from backend.app.schemas.obligation import (
    ObligationCreate,
    ObligationUpdate,
    ObligationStatusUpdate,
    ObligationOut,
)
from backend.app.core.auth import get_current_user


router = APIRouter()


# ============================================================
# CREATE OBLIGATION
# ============================================================

@router.post(
    "/",
    response_model=ObligationOut,
    status_code=201
)
def create_obligation(
    obligation_data: ObligationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    # Check contract
    contract = db.query(Contract).filter(
        Contract.id == obligation_data.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found"
        )

    # Check assigned user
    user = db.query(User).filter(
        User.id == obligation_data.assigned_to
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Assigned user not found"
        )

    # Create obligation
    new_obligation = Obligation(
        contract_id=obligation_data.contract_id,
        title=obligation_data.title,
        description=obligation_data.description,
        obligation_type=obligation_data.obligation_type,
        due_date=obligation_data.due_date,
        assigned_to=obligation_data.assigned_to,
        status="Pending"
    )

    db.add(new_obligation)
    db.commit()
    db.refresh(new_obligation)

    return new_obligation


# ============================================================
# GET ALL OBLIGATIONS
# ============================================================

@router.get(
    "/",
    response_model=list[ObligationOut]
)
def get_obligations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    obligations = db.query(Obligation).all()

    return obligations


# ============================================================
# GET OBLIGATIONS FOR CONTRACT
# ============================================================

@router.get(
    "/contracts/{contract_id}/obligations",
    response_model=list[ObligationOut]
)
def get_contract_obligations(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    # Check contract
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found"
        )

    obligations = db.query(Obligation).filter(
        Obligation.contract_id == contract_id
    ).all()

    return obligations


# ============================================================
# UPDATE OBLIGATION
# ============================================================

@router.put(
    "/{obligation_id}",
    response_model=ObligationOut
)
def update_obligation(
    obligation_id: int,
    obligation_data: ObligationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail="Obligation not found"
        )

    # Check assigned user if changing assignment
    if obligation_data.assigned_to is not None:

        user = db.query(User).filter(
            User.id == obligation_data.assigned_to
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Assigned user not found"
            )

        obligation.assigned_to = obligation_data.assigned_to

    if obligation_data.title is not None:
        obligation.title = obligation_data.title

    if obligation_data.description is not None:
        obligation.description = obligation_data.description

    if obligation_data.obligation_type is not None:
        obligation.obligation_type = obligation_data.obligation_type

    if obligation_data.due_date is not None:
        obligation.due_date = obligation_data.due_date

    db.commit()
    db.refresh(obligation)

    return obligation


# ============================================================
# UPDATE OBLIGATION STATUS
# ============================================================

@router.patch(
    "/{obligation_id}/status",
    response_model=ObligationOut
)
def update_obligation_status(
    obligation_id: int,
    status_data: ObligationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail="Obligation not found"
        )

    allowed_statuses = [
        "Pending",
        "In Progress",
        "Completed",
        "Delayed",
        "Overdue"
    ]

    if status_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid obligation status"
        )

    current_status = obligation.status
    new_status = status_data.status

    valid_transitions = {
        "Pending": ["In Progress", "Overdue"],
        "In Progress": ["Completed", "Delayed", "Overdue"],
        "Delayed": ["In Progress", "Completed", "Overdue"],
        "Overdue": ["In Progress", "Completed"],
        "Completed": []
    }

    if new_status not in valid_transitions.get(current_status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition from {current_status} to {new_status}"
        )

    obligation.status = new_status

    if new_status == "Completed":
        obligation.completion_date = date.today()

    db.commit()
    db.refresh(obligation)

    return obligation


# ============================================================
# COMPLETE OBLIGATION
# ============================================================

@router.post(
    "/{obligation_id}/complete",
    response_model=ObligationOut
)
def complete_obligation(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail="Obligation not found"
        )

    if obligation.status == "Completed":
        raise HTTPException(
            status_code=400,
            detail="Obligation is already completed"
        )

    obligation.status = "Completed"
    obligation.completion_date = date.today()

    db.commit()
    db.refresh(obligation)

    return obligation


# ============================================================
# OVERDUE OBLIGATIONS
# ============================================================

@router.get(
    "/overdue/list",
    response_model=list[ObligationOut]
)
def get_overdue_obligations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    today = date.today()

    obligations = db.query(Obligation).filter(
        Obligation.due_date < today,
        Obligation.status != "Completed"
    ).all()

    return obligations
#==============================================================
# GET BY ID 
#==============================================================

@router.get(
    "/{obligation_id}",
    response_model=ObligationOut
)
def get_obligation(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail="Obligation not found"
        )

    return obligation

