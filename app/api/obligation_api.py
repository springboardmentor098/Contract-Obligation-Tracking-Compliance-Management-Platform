from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.obligation import Obligation
from app.models.contract import Contract
from app.models.user import User
from app.schemas.obligation_schema import (
    ObligationCreate,
    ObligationUpdate,
    ObligationStatusUpdate,
    ObligationResponse
)
from app.core.auth import get_current_user

router = APIRouter(
    prefix="/obligations",
    tags=["Obligations"]
)


# ---------------- CREATE OBLIGATION ----------------

@router.post(
    "",
    response_model=ObligationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_obligation(
    obligation_data: ObligationCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(
        Contract.id == obligation_data.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found"
        )

    user = db.query(User).filter(
        User.id == obligation_data.assigned_to
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Assigned user not found"
        )

    obligation = Obligation(
        contract_id=obligation_data.contract_id,
        title=obligation_data.title,
        description=obligation_data.description,
        obligation_type=obligation_data.obligation_type,
        due_date=obligation_data.due_date,
        assigned_to=obligation_data.assigned_to,
        status="Pending"
    )

    db.add(obligation)
    db.commit()
    db.refresh(obligation)

    return obligation


# ---------------- GET ALL OBLIGATIONS ----------------

@router.get(
    "",
    response_model=list[ObligationResponse]
)
def get_obligations(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Obligation).all()


# ---------------- GET OBLIGATION BY ID ----------------

@router.get(
    "/{obligation_id}",
    response_model=ObligationResponse
)
def get_obligation(
    obligation_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
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


# ---------------- GET OBLIGATIONS FOR A CONTRACT ----------------

@router.get(
    "/contract/{contract_id}",
    response_model=list[ObligationResponse]
)
def get_contract_obligations(
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

    return db.query(Obligation).filter(
        Obligation.contract_id == contract_id
    ).all()


# ---------------- UPDATE OBLIGATION ----------------

@router.put(
    "/{obligation_id}",
    response_model=ObligationResponse
)
def update_obligation(
    obligation_id: int,
    obligation_data: ObligationUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail="Obligation not found"
        )

    update_data = obligation_data.model_dump(exclude_unset=True)

    if "assigned_to" in update_data:
        user = db.query(User).filter(
            User.id == update_data["assigned_to"]
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Assigned user not found"
            )

    for key, value in update_data.items():
        setattr(obligation, key, value)

    db.commit()
    db.refresh(obligation)

    return obligation


# ---------------- UPDATE STATUS ----------------

@router.patch(
    "/{obligation_id}/status",
    response_model=ObligationResponse
)
def update_status(
    obligation_id: int,
    status_data: ObligationStatusUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail="Obligation not found"
        )

    workflow = {
        "Pending": ["In Progress"],
        "In Progress": ["Completed"],
        "Completed": [],
        "Delayed": ["Completed"],
        "Overdue": ["Completed"]
    }

    current = obligation.status
    new = status_data.status

    if new not in workflow.get(current, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition from '{current}' to '{new}'"
        )

    obligation.status = new

    if new == "Completed":
        obligation.completion_date = date.today()

    db.commit()
    db.refresh(obligation)

    return obligation