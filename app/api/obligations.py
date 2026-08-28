from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.user import User
from app.schemas.obligation import (
    ObligationCreate,
    ObligationResponse,
    ObligationStatusUpdate,
    ObligationUpdate,
    VALID_OBLIGATION_STATUSES,
    VALID_OBLIGATION_TYPES,
)

router = APIRouter(
    tags=["Obligations"]
)


def evaluate_overdue_status(obligation: Obligation) -> Obligation:
    """Dynamically evaluate if an obligation is overdue based on due_date and current status."""
    if obligation.status != "Completed" and obligation.due_date is not None:
        if obligation.due_date < date.today():
            obligation.status = "Overdue"
    return obligation


@router.post(
    "/obligations",
    response_model=ObligationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Obligation",
    description="Creates a new contractual obligation and associates it with a contract and responsible user."
)
def create_obligation(
    obligation_in: ObligationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new obligation."""
    # 1. Verify contract exists
    contract = db.query(Contract).filter(Contract.id == obligation_in.contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {obligation_in.contract_id} not found."
        )

    # 2. Verify assigned user exists
    assigned_user = db.query(User).filter(
        (User.user_id == obligation_in.assigned_to) | (User.id == obligation_in.assigned_to)
    ).first()
    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assigned user with ID {obligation_in.assigned_to} not found."
        )

    # 3. Validate obligation_type if needed
    type_clean = obligation_in.obligation_type.strip()
    
    # Initial status is Pending
    initial_status = "Pending"
    if obligation_in.due_date and obligation_in.due_date < date.today():
        initial_status = "Overdue"

    new_obligation = Obligation(
        contract_id=obligation_in.contract_id,
        title=obligation_in.title.strip(),
        description=obligation_in.description.strip() if obligation_in.description else None,
        obligation_type=type_clean,
        due_date=obligation_in.due_date,
        assigned_to=obligation_in.assigned_to,
        status=initial_status
    )

    db.add(new_obligation)
    db.commit()
    db.refresh(new_obligation)

    return evaluate_overdue_status(new_obligation)


@router.get(
    "/obligations",
    response_model=List[ObligationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get All Obligations",
    description="Retrieves all contractual obligations with overdue detection."
)
def get_all_obligations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all obligations."""
    obligations = db.query(Obligation).all()
    updated_obligations = [evaluate_overdue_status(ob) for ob in obligations]
    db.commit()
    return updated_obligations


@router.get(
    "/obligations/{obligation_id}",
    response_model=ObligationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Obligation by ID",
    description="Retrieves a specific obligation by its unique ID."
)
def get_obligation_by_id(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific obligation details."""
    obligation = db.query(Obligation).filter(
        (Obligation.id == obligation_id) | (Obligation.obligation_id == obligation_id)
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Obligation with ID {obligation_id} not found."
        )

    evaluated = evaluate_overdue_status(obligation)
    db.commit()
    return evaluated


@router.get(
    "/contracts/{contract_id}/obligations",
    response_model=List[ObligationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Obligations for a Contract",
    description="Retrieves all obligations associated with a specific contract."
)
def get_contract_obligations(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get obligations for a particular contract."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found."
        )

    obligations = db.query(Obligation).filter(Obligation.contract_id == contract_id).all()
    updated_obligations = [evaluate_overdue_status(ob) for ob in obligations]
    db.commit()
    return updated_obligations


@router.put(
    "/obligations/{obligation_id}",
    response_model=ObligationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Obligation",
    description="Allows authorized users to update obligation details."
)
def update_obligation(
    obligation_id: int,
    obligation_in: ObligationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update obligation details."""
    obligation = db.query(Obligation).filter(
        (Obligation.id == obligation_id) | (Obligation.obligation_id == obligation_id)
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Obligation with ID {obligation_id} not found."
        )

    if obligation_in.assigned_to is not None:
        assigned_user = db.query(User).filter(
            (User.user_id == obligation_in.assigned_to) | (User.id == obligation_in.assigned_to)
        ).first()
        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assigned user with ID {obligation_in.assigned_to} not found."
            )
        obligation.assigned_to = obligation_in.assigned_to

    if obligation_in.title is not None:
        obligation.title = obligation_in.title.strip()
    if obligation_in.description is not None:
        obligation.description = obligation_in.description.strip()
    if obligation_in.obligation_type is not None:
        obligation.obligation_type = obligation_in.obligation_type.strip()
    if obligation_in.due_date is not None:
        obligation.due_date = obligation_in.due_date

    obligation.updated_at = datetime.utcnow()
    evaluated = evaluate_overdue_status(obligation)
    db.commit()
    db.refresh(evaluated)

    return evaluated


@router.patch(
    "/obligations/{obligation_id}/status",
    response_model=ObligationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Obligation Status",
    description="Updates the status of an obligation (e.g., Pending -> In Progress -> Completed)."
)
def update_obligation_status(
    obligation_id: int,
    status_in: ObligationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update obligation status."""
    obligation = db.query(Obligation).filter(
        (Obligation.id == obligation_id) | (Obligation.obligation_id == obligation_id)
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Obligation with ID {obligation_id} not found."
        )

    new_status = status_in.status.strip()
    if new_status not in VALID_OBLIGATION_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{new_status}'. Supported statuses: {', '.join(VALID_OBLIGATION_STATUSES)}."
        )

    obligation.status = new_status
    if new_status == "Completed" and not obligation.completion_date:
        obligation.completion_date = date.today()

    obligation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(obligation)

    return obligation


@router.post(
    "/obligations/{obligation_id}/complete",
    response_model=ObligationResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete Obligation",
    description="Marks an obligation as Completed and records backend completion date."
)
def complete_obligation(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete an obligation and record current completion date."""
    obligation = db.query(Obligation).filter(
        (Obligation.id == obligation_id) | (Obligation.obligation_id == obligation_id)
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Obligation with ID {obligation_id} not found."
        )

    obligation.status = "Completed"
    obligation.completion_date = date.today()
    obligation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(obligation)

    return obligation
