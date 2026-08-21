from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.obligation import Obligation
from app.models.contract import Contract
from app.models.user import User
from app.schemas.obligation import (
    ObligationCreate,
    ObligationUpdate,
    ObligationStatusUpdate,
    ObligationResponse,
)
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/obligations",
    tags=["Obligations"]
)


ALLOWED_STATUSES = {
    "Pending",
    "In Progress",
    "Completed",
    "Delayed",
    "Overdue"
}

ALLOWED_TYPES = {
    "Payment Obligation",
    "Delivery Commitment",
    "Reporting Requirement",
    "Renewal Condition",
    "Service Level Agreement",
    "Legal Compliance Requirement"
}


def get_obligation_or_404(
    obligation_id: int,
    db: Session
):
    obligation = (
        db.query(Obligation)
        .filter(Obligation.id == obligation_id)
        .first()
    )

    if obligation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found"
        )

    return obligation


def check_overdue(obligation: Obligation):
    if (
        obligation.status in {"Pending", "In Progress", "Delayed"}
        and obligation.due_date < date.today()
    ):
        obligation.status = "Overdue"


@router.post(
    "/",
    response_model=ObligationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_obligation(
    obligation_data: ObligationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == obligation_data.contract_id)
        .first()
    )

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    assigned_user = (
        db.query(User)
        .filter(User.id == obligation_data.assigned_to)
        .first()
    )

    if assigned_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )

    if obligation_data.obligation_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid obligation type"
        )

    obligation = Obligation(
        contract_id=obligation_data.contract_id,
        assigned_to=obligation_data.assigned_to,
        title=obligation_data.title,
        description=obligation_data.description,
        obligation_type=obligation_data.obligation_type,
        due_date=obligation_data.due_date,
        status="Pending"
    )

    db.add(obligation)
    db.commit()
    db.refresh(obligation)

    return obligation


@router.get(
    "/",
    response_model=list[ObligationResponse]
)
def get_obligations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obligations = (
        db.query(Obligation)
        .join(Contract, Obligation.contract_id == Contract.id)
        .filter(
            (Contract.owner_id == current_user.id)
            | (Obligation.assigned_to == current_user.id)
        )
        .all()
    )

    for obligation in obligations:
        check_overdue(obligation)

    db.commit()

    return obligations


@router.get(
    "/{obligation_id}",
    response_model=ObligationResponse
)
def get_obligation(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obligation = get_obligation_or_404(obligation_id, db)

    contract = (
        db.query(Contract)
        .filter(Contract.id == obligation.contract_id)
        .first()
    )

    if (
        contract.owner_id != current_user.id
        and obligation.assigned_to != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this obligation"
        )

    check_overdue(obligation)
    db.commit()
    db.refresh(obligation)

    return obligation


@router.get(
    "/contract/{contract_id}/obligations",
    response_model=list[ObligationResponse]
)
def get_contract_obligations(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if contract.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this contract"
        )

    obligations = (
        db.query(Obligation)
        .filter(Obligation.contract_id == contract_id)
        .all()
    )

    for obligation in obligations:
        check_overdue(obligation)

    db.commit()

    return obligations


@router.put(
    "/{obligation_id}",
    response_model=ObligationResponse
)
def update_obligation(
    obligation_id: int,
    obligation_data: ObligationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obligation = get_obligation_or_404(obligation_id, db)

    contract = (
        db.query(Contract)
        .filter(Contract.id == obligation.contract_id)
        .first()
    )

    if (
        contract.owner_id != current_user.id
        and obligation.assigned_to != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this obligation"
        )

    update_data = obligation_data.model_dump(exclude_unset=True)

    if "assigned_to" in update_data:
        assigned_user = (
            db.query(User)
            .filter(User.id == update_data["assigned_to"])
            .first()
        )

        if assigned_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found"
            )

    if (
        "obligation_type" in update_data
        and update_data["obligation_type"] not in ALLOWED_TYPES
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid obligation type"
        )

    for field, value in update_data.items():
        setattr(obligation, field, value)

    db.commit()
    db.refresh(obligation)

    return obligation


@router.patch(
    "/{obligation_id}/status",
    response_model=ObligationResponse
)
def update_obligation_status(
    obligation_id: int,
    status_data: ObligationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obligation = get_obligation_or_404(obligation_id, db)

    contract = (
        db.query(Contract)
        .filter(Contract.id == obligation.contract_id)
        .first()
    )

    if (
        contract.owner_id != current_user.id
        and obligation.assigned_to != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this obligation"
        )

    new_status = status_data.status

    if new_status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid obligation status"
        )

    current_status = obligation.status

    valid_transitions = {
        "Pending": {"In Progress", "Delayed", "Overdue"},
        "In Progress": {"Completed", "Delayed", "Overdue"},
        "Delayed": {"In Progress", "Completed", "Overdue"},
        "Overdue": {"In Progress", "Completed"},
        "Completed": set()
    }

    if new_status not in valid_transitions.get(current_status, set()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition: {current_status} -> {new_status}"
        )

    obligation.status = new_status

    db.commit()
    db.refresh(obligation)

    return obligation


@router.post(
    "/{obligation_id}/complete",
    response_model=ObligationResponse
)
def complete_obligation(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obligation = get_obligation_or_404(obligation_id, db)

    contract = (
        db.query(Contract)
        .filter(Contract.id == obligation.contract_id)
        .first()
    )

    if (
        contract.owner_id != current_user.id
        and obligation.assigned_to != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to complete this obligation"
        )

    if obligation.status == "Completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Obligation is already completed"
        )

    if obligation.status == "Overdue":
        # Allow completion of overdue obligations.
        obligation.status = "Completed"
    elif obligation.status in {"Pending", "In Progress", "Delayed"}:
        obligation.status = "Completed"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Obligation cannot be completed from its current status"
        )

    obligation.completion_date = date.today()

    db.commit()
    db.refresh(obligation)

    return obligation