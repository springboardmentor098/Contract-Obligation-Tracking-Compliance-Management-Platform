from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.user import User
from app.schemas.obligation import (
    ObligationCreate,
    ObligationUpdate,
    ObligationStatusUpdate,
    ObligationResponse,
    OBLIGATION_TYPES,
    OBLIGATION_STATUSES,
)
from app.utils.authorization import get_current_user


router = APIRouter(
    prefix="/obligations",
    tags=["Obligations"]
)

contract_obligations_router = APIRouter(
    prefix="/contracts",
    tags=["Obligations"]
)


MANAGER_ROLES = {
    "Administrator",
    "Legal Manager",
    "Contract Manager",
}


def get_obligation_or_404(
    obligation_id: int,
    db: Session
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if obligation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found"
        )

    return obligation


def get_contract_or_404(
    contract_id: int,
    db: Session
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return contract


def mark_overdue(obligation: Obligation):
    if (
        obligation.status != "Completed"
        and obligation.due_date < date.today()
    ):
        obligation.status = "Overdue"


def can_manage_obligation(
    current_user: dict,
    obligation: Obligation
):
    user_id = current_user["user_id"]
    role = current_user.get("role", "")

    return (
        role in MANAGER_ROLES
        or obligation.assigned_to == user_id
    )


@router.post(
    "",
    response_model=ObligationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_obligation(
    obligation_data: ObligationCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = get_contract_or_404(
        obligation_data.contract_id,
        db
    )

    assigned_user = db.query(User).filter(
        User.id == obligation_data.assigned_to
    ).first()

    if assigned_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )

    if obligation_data.obligation_type not in OBLIGATION_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid obligation type"
        )

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    obligation = Obligation(
        contract_id=contract.id,
        title=obligation_data.title,
        description=obligation_data.description,
        obligation_type=obligation_data.obligation_type,
        due_date=obligation_data.due_date,
        assigned_to=obligation_data.assigned_to,
        status="Pending",
        completion_date=None,
        created_at=now,
        updated_at=now,
    )

    db.add(obligation)
    db.commit()
    db.refresh(obligation)

    return obligation


@router.get(
    "",
    response_model=list[ObligationResponse]
)
def get_obligations(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    obligations = db.query(Obligation).all()

    changed = False

    for obligation in obligations:
        old_status = obligation.status
        mark_overdue(obligation)

        if obligation.status != old_status:
            obligation.updated_at = datetime.now(
                timezone.utc
            ).replace(tzinfo=None)
            changed = True

    if changed:
        db.commit()

    return obligations


@router.get(
    "/{obligation_id}",
    response_model=ObligationResponse
)
def get_obligation(
    obligation_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    obligation = get_obligation_or_404(
        obligation_id,
        db
    )

    old_status = obligation.status
    mark_overdue(obligation)

    if obligation.status != old_status:
        obligation.updated_at = datetime.now(
            timezone.utc
        ).replace(tzinfo=None)
        db.commit()
        db.refresh(obligation)

    return obligation


@router.put(
    "/{obligation_id}",
    response_model=ObligationResponse
)
def update_obligation(
    obligation_id: int,
    obligation_data: ObligationUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    obligation = get_obligation_or_404(
        obligation_id,
        db
    )

    if not can_manage_obligation(
        current_user,
        obligation
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this obligation"
        )

    update_data = obligation_data.model_dump(
        exclude_unset=True
    )

    if "obligation_type" in update_data:
        if update_data["obligation_type"] not in OBLIGATION_TYPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid obligation type"
            )

    if "assigned_to" in update_data:
        user = db.query(User).filter(
            User.id == update_data["assigned_to"]
        ).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found"
            )

    for field, value in update_data.items():
        setattr(obligation, field, value)

    obligation.updated_at = datetime.now(
        timezone.utc
    ).replace(tzinfo=None)

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
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    obligation = get_obligation_or_404(
        obligation_id,
        db
    )

    if not can_manage_obligation(
        current_user,
        obligation
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update obligation status"
        )

    new_status = status_data.status

    if new_status not in OBLIGATION_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid obligation status"
        )

    allowed_transitions = {
        "Pending": {"In Progress", "Delayed", "Overdue"},
        "In Progress": {"Completed", "Delayed", "Overdue"},
        "Delayed": {"In Progress", "Completed", "Overdue"},
        "Overdue": {"In Progress", "Completed"},
        "Completed": set(),
    }

    if new_status not in allowed_transitions.get(
        obligation.status,
        set()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status transition: "
                f"{obligation.status} -> {new_status}"
            )
        )

    obligation.status = new_status
    obligation.updated_at = datetime.now(
        timezone.utc
    ).replace(tzinfo=None)

    if new_status == "Completed":
        obligation.completion_date = datetime.now(
            timezone.utc
        ).replace(tzinfo=None)

    db.commit()
    db.refresh(obligation)

    return obligation


@router.post(
    "/{obligation_id}/complete",
    response_model=ObligationResponse
)
def complete_obligation(
    obligation_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    obligation = get_obligation_or_404(
        obligation_id,
        db
    )

    if not can_manage_obligation(
        current_user,
        obligation
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

    obligation.status = "Completed"
    obligation.completion_date = datetime.now(
        timezone.utc
    ).replace(tzinfo=None)
    obligation.updated_at = datetime.now(
        timezone.utc
    ).replace(tzinfo=None)

    db.commit()
    db.refresh(obligation)

    return obligation


@contract_obligations_router.get(
    "/{contract_id}/obligations",
    response_model=list[ObligationResponse]
)
def get_contract_obligations(
    contract_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    get_contract_or_404(contract_id, db)

    obligations = db.query(Obligation).filter(
        Obligation.contract_id == contract_id
    ).all()

    changed = False

    for obligation in obligations:
        old_status = obligation.status
        mark_overdue(obligation)

        if obligation.status != old_status:
            obligation.updated_at = datetime.now(
                timezone.utc
            ).replace(tzinfo=None)
            changed = True

    if changed:
        db.commit()

    return obligations
