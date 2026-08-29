from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.contract import Contract
from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.obligation import Obligation
from app.models.user import User
from app.schemas.obligation import (
    ObligationCreate,
    ObligationResponse,
    ObligationStatusUpdate,
    ObligationUpdate,
)

router = APIRouter(
    prefix="/obligations",
    tags=["Obligations"],
)


@router.post(
    "",
    response_model=ObligationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_obligation(
    obligation_data: ObligationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contract = db.query(Contract).filter(
    Contract.id == obligation_data.contract_id
).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found",
        )

    assigned_user = db.query(User).filter(
        User.id == obligation_data.assigned_to
    ).first()

    if not assigned_user:
        raise HTTPException(
            status_code=404,
            detail="Assigned user not found",
        )

    obligation = Obligation(
        contract_id=obligation_data.contract_id,
        title=obligation_data.title,
        description=obligation_data.description,
        obligation_type=obligation_data.obligation_type,
        due_date=obligation_data.due_date,
        assigned_to=obligation_data.assigned_to,
        status="Pending",
    )

    db.add(obligation)
    db.commit()
    db.refresh(obligation)

    return obligation


@router.get(
    "",
    response_model=list[ObligationResponse],
)
def get_obligations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obligations = db.query(Obligation).all()

    for obligation in obligations:
        if (
            obligation.status in ["Pending", "In Progress"]
            and obligation.due_date < date.today()
        ):
            obligation.status = "Overdue"

    db.commit()

    return obligations


@router.get(
    "/{obligation_id}",
    response_model=ObligationResponse,
)
def get_obligation(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail="Obligation not found",
        )

    if (
        obligation.status in ["Pending", "In Progress"]
        and obligation.due_date < date.today()
    ):
        obligation.status = "Overdue"
        db.commit()
        db.refresh(obligation)

    return obligation


@router.put(
    "/{obligation_id}",
    response_model=ObligationResponse,
)
def update_obligation(
    obligation_id: int,
    obligation_data: ObligationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail="Obligation not found",
        )

    assigned_user = None

    if obligation_data.assigned_to is not None:
        assigned_user = db.query(User).filter(
            User.id == obligation_data.assigned_to
        ).first()

        if not assigned_user:
            raise HTTPException(
                status_code=404,
                detail="Assigned user not found",
            )

    update_data = obligation_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(obligation, field, value)

    db.commit()
    db.refresh(obligation)

    return obligation


@router.patch(
    "/{obligation_id}/status",
    response_model=ObligationResponse,
)
def update_obligation_status(
    obligation_id: int,
    status_data: ObligationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail="Obligation not found",
        )

    allowed_statuses = {
        "Pending",
        "In Progress",
        "Completed",
        "Overdue",
    }

    if status_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid obligation status",
        )

    obligation.status = status_data.status

    if status_data.status == "Completed":
        obligation.completion_date = date.today()

    db.commit()
    db.refresh(obligation)

    return obligation


@router.post(
    "/{obligation_id}/complete",
    response_model=ObligationResponse,
)
def complete_obligation(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail="Obligation not found",
        )

    if obligation.status == "Completed":
        raise HTTPException(
            status_code=400,
            detail="Obligation is already completed",
        )

    obligation.status = "Completed"
    obligation.completion_date = date.today()

    db.commit()
    db.refresh(obligation)

    return obligation