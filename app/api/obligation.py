from datetime import date
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.user import User
from app.schemas.obligation_schema import (
    ObligationCreate,
    ObligationUpdate,
    ObligationStatusUpdate,
    ObligationResponse,
)
from app.middleware.auth import require_roles


router = APIRouter(
    prefix="/obligations",
    tags=["Obligations"]
)


# ============================================================
# COMMON AUTHORIZED ROLES
# ============================================================

VIEW_ROLES = (
    "Administrator",
    "Legal Manager",
    "Compliance Officer",
    "Contract Manager",
    "Department Head",
    "Employee",
)

MANAGE_ROLES = (
    "Administrator",
    "Legal Manager",
    "Contract Manager",
)

PROGRESS_ROLES = (
    "Administrator",
    "Legal Manager",
    "Contract Manager",
    "Compliance Officer",
    "Department Head",
    "Employee",
)


# ============================================================
# OVERDUE DETECTION HELPER
# ============================================================

def mark_overdue(obligation: Obligation) -> bool:
    """
    Mark an obligation as Overdue when its due date has passed
    and it has not been completed.

    Returns True if the status was changed.
    """

    if (
        obligation.status != "Completed"
        and obligation.due_date
        and obligation.due_date < date.today()
    ):
        if obligation.status != "Overdue":
            obligation.status = "Overdue"
            return True

    return False


def refresh_overdue_status(
    db: Session,
    obligation: Obligation
):
    """
    Check and persist overdue status for one obligation.
    """

    changed = mark_overdue(obligation)

    if changed:
        db.commit()
        db.refresh(obligation)

    return obligation


# ============================================================
# CREATE OBLIGATION
# Administrator, Legal Manager, Contract Manager
# ============================================================

@router.post(
    "",
    response_model=ObligationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_obligation(
    obligation_data: ObligationCreate,
    current_user: dict = Depends(
        require_roles(*MANAGE_ROLES)
    ),
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Verify contract
    # --------------------------------------------------------

    contract = db.query(Contract).filter(
        Contract.id == obligation_data.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # --------------------------------------------------------
    # Verify assigned user
    # --------------------------------------------------------

    assigned_user = db.query(User).filter(
        User.id == obligation_data.assigned_to,
        User.is_active == True
    ).first()

    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found or inactive"
        )

    # --------------------------------------------------------
    # Create obligation
    # --------------------------------------------------------

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


# ============================================================
# GET ALL OBLIGATIONS
# ============================================================

@router.get(
    "",
    response_model=list[ObligationResponse],
    status_code=status.HTTP_200_OK,
)
def get_obligations(
    current_user: dict = Depends(
        require_roles(*VIEW_ROLES)
    ),
    db: Session = Depends(get_db)
):

    obligations = db.query(Obligation).all()

    # Detect overdue obligations
    changed = False

    for obligation in obligations:
        if mark_overdue(obligation):
            changed = True

    if changed:
        db.commit()

    return obligations


# ============================================================
# GET OVERDUE OBLIGATIONS
# ============================================================

@router.get(
    "/overdue",
    response_model=list[ObligationResponse],
    status_code=status.HTTP_200_OK,
)
def get_overdue_obligations(
    current_user: dict = Depends(
        require_roles(*VIEW_ROLES)
    ),
    db: Session = Depends(get_db)
):

    today = date.today()

    # --------------------------------------------------------
    # Find all non-completed obligations whose due date passed
    # --------------------------------------------------------

    overdue_obligations = db.query(Obligation).filter(
        Obligation.due_date < today,
        Obligation.status != "Completed"
    ).all()

    # --------------------------------------------------------
    # Update status to Overdue
    # --------------------------------------------------------

    changed = False

    for obligation in overdue_obligations:

        if obligation.status != "Overdue":
            obligation.status = "Overdue"
            changed = True

    if changed:
        db.commit()

    return overdue_obligations


# ============================================================
# GET OBLIGATION BY ID
# ============================================================

@router.get(
    "/{obligation_id}",
    response_model=ObligationResponse,
    status_code=status.HTTP_200_OK,
)
def get_obligation(
    obligation_id: int,
    current_user: dict = Depends(
        require_roles(*VIEW_ROLES)
    ),
    db: Session = Depends(get_db)
):

    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found"
        )

    return refresh_overdue_status(
        db,
        obligation
    )


# ============================================================
# GET OBLIGATIONS FOR SPECIFIC CONTRACT
# ============================================================

@router.get(
    "/contract/{contract_id}",
    response_model=list[ObligationResponse],
    status_code=status.HTTP_200_OK,
)
def get_contract_obligations(
    contract_id: int,
    current_user: dict = Depends(
        require_roles(*VIEW_ROLES)
    ),
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Verify contract exists
    # --------------------------------------------------------

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    obligations = db.query(Obligation).filter(
        Obligation.contract_id == contract_id
    ).all()

    changed = False

    for obligation in obligations:
        if mark_overdue(obligation):
            changed = True

    if changed:
        db.commit()

    return obligations


# ============================================================
# UPDATE OBLIGATION
# Administrator, Legal Manager, Contract Manager
# ============================================================

@router.put(
    "/{obligation_id}",
    response_model=ObligationResponse,
    status_code=status.HTTP_200_OK,
)
def update_obligation(
    obligation_id: int,
    obligation_data: ObligationUpdate,
    current_user: dict = Depends(
        require_roles(*MANAGE_ROLES)
    ),
    db: Session = Depends(get_db)
):

    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found"
        )

    # --------------------------------------------------------
    # Verify assigned user
    # --------------------------------------------------------

    assigned_user = db.query(User).filter(
        User.id == obligation_data.assigned_to,
        User.is_active == True
    ).first()

    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found or inactive"
        )

    # --------------------------------------------------------
    # Update allowed fields
    # --------------------------------------------------------

    obligation.title = obligation_data.title
    obligation.description = obligation_data.description
    obligation.obligation_type = obligation_data.obligation_type
    obligation.due_date = obligation_data.due_date
    obligation.assigned_to = obligation_data.assigned_to

    db.commit()
    db.refresh(obligation)

    return refresh_overdue_status(
        db,
        obligation
    )


# ============================================================
# UPDATE OBLIGATION STATUS
# ============================================================

@router.patch(
    "/{obligation_id}/status",
    response_model=ObligationResponse,
    status_code=status.HTTP_200_OK,
)
def update_obligation_status(
    obligation_id: int,
    status_data: ObligationStatusUpdate,
    current_user: dict = Depends(
        require_roles(*PROGRESS_ROLES)
    ),
    db: Session = Depends(get_db)
):

    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found"
        )

    current_status = obligation.status
    new_status = status_data.status

    # --------------------------------------------------------
    # Allowed workflow transitions
    # --------------------------------------------------------

    allowed_transitions = {
        "Pending": [
            "In Progress",
            "Delayed",
            "Overdue"
        ],

        "In Progress": [
            "Completed",
            "Delayed",
            "Overdue"
        ],

        "Delayed": [
            "In Progress",
            "Completed",
            "Overdue"
        ],

        "Overdue": [
            "In Progress",
            "Completed"
        ],

        "Completed": []
    }

    if new_status not in allowed_transitions.get(
        current_status,
        []
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status transition: "
                f"{current_status} -> {new_status}"
            )
        )

    obligation.status = new_status

    # --------------------------------------------------------
    # Completion date
    # --------------------------------------------------------

    if new_status == "Completed":
        obligation.completion_date = date.today()

    elif current_status == "Completed":
        obligation.completion_date = None

    db.commit()
    db.refresh(obligation)

    return obligation


# ============================================================
# COMPLETE OBLIGATION
#
# Backend determines completion date.
# Client cannot provide completion date.
# ============================================================

@router.post(
    "/{obligation_id}/complete",
    response_model=ObligationResponse,
    status_code=status.HTTP_200_OK,
)
def complete_obligation(
    obligation_id: int,
    current_user: dict = Depends(
        require_roles(*PROGRESS_ROLES)
    ),
    db: Session = Depends(get_db)
):

    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found"
        )

    if obligation.status == "Completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Obligation is already completed"
        )

    obligation.status = "Completed"
    obligation.completion_date = date.today()

    db.commit()
    db.refresh(obligation)

    return obligation


# ============================================================
# ASSIGN / REASSIGN OBLIGATION
# ============================================================

@router.patch(
    "/{obligation_id}/assign",
    response_model=ObligationResponse,
    status_code=status.HTTP_200_OK,
)
def assign_obligation(
    obligation_id: int,
    assigned_to: int,
    current_user: dict = Depends(
        require_roles(*MANAGE_ROLES)
    ),
    db: Session = Depends(get_db)
):

    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found"
        )

    assigned_user = db.query(User).filter(
        User.id == assigned_to,
        User.is_active == True
    ).first()

    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found or inactive"
        )

    obligation.assigned_to = assigned_to

    db.commit()
    db.refresh(obligation)

    return obligation
