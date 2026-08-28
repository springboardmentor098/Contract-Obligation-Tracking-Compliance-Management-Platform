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
    ObligationComplete,
    ObligationResponse,
)

from app.schemas.permissions import Permission
from app.core.dependencies import (
    get_current_user,
    require_permission,
)


router = APIRouter(
    prefix="/obligations",
    tags=["Obligations"]
)


# ============================================================
# 1. POST - Create Obligation
# ============================================================

@router.post(
    "",
    response_model=ObligationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_obligation(
    obligation_data: ObligationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.MANAGE_OBLIGATIONS)
    )
):
    # Check whether contract exists
    contract = (
        db.query(Contract)
        .filter(Contract.id == obligation_data.contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Contract with ID "
                f"{obligation_data.contract_id} not found"
            )
        )

    # Check whether assigned user exists
    assigned_user = (
        db.query(User)
        .filter(User.id == obligation_data.assigned_to)
        .first()
    )

    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"User with ID "
                f"{obligation_data.assigned_to} not found"
            )
        )

    # Create obligation
    obligation = Obligation(
        contract_id=obligation_data.contract_id,
        title=obligation_data.title,
        description=obligation_data.description,
        obligation_type=obligation_data.obligation_type,
        due_date=obligation_data.due_date,
        assigned_to=obligation_data.assigned_to,
        status="Pending",
        progress=0,
    )

    db.add(obligation)
    db.commit()
    db.refresh(obligation)

    return obligation


# ============================================================
# 2. GET - Get All Obligations
# ============================================================

@router.get(
    "",
    response_model=list[ObligationResponse],
    status_code=status.HTTP_200_OK
)
def get_obligations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Obligation).all()


# ============================================================
# 3. GET - Get Overdue Obligations
# ============================================================

@router.get(
    "/overdue",
    response_model=list[ObligationResponse],
    status_code=status.HTTP_200_OK
)
def get_overdue_obligations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()

    overdue_obligations = (
        db.query(Obligation)
        .filter(
            Obligation.due_date < today,
            Obligation.status != "Completed"
        )
        .all()
    )

    return overdue_obligations


# ============================================================
# 4. GET - Obligation Dashboard
# ============================================================

@router.get(
    "/dashboard",
    status_code=status.HTTP_200_OK
)
def get_obligation_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()

    obligations = db.query(Obligation).all()

    total_obligations = len(obligations)

    pending_count = sum(
        1 for obligation in obligations
        if obligation.status == "Pending"
    )

    in_progress_count = sum(
        1 for obligation in obligations
        if obligation.status == "In Progress"
    )

    completed_count = sum(
        1 for obligation in obligations
        if obligation.status == "Completed"
    )

    overdue_count = sum(
        1 for obligation in obligations
        if (
            obligation.due_date < today
            and obligation.status != "Completed"
        )
    )

    return {
        "total_obligations": total_obligations,
        "pending": pending_count,
        "in_progress": in_progress_count,
        "completed": completed_count,
        "overdue": overdue_count
    }


# ============================================================
# 5. GET - Get Obligation by ID
# ============================================================

@router.get(
    "/{obligation_id}",
    response_model=ObligationResponse,
    status_code=status.HTTP_200_OK
)
def get_obligation_by_id(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obligation = (
        db.query(Obligation)
        .filter(Obligation.id == obligation_id)
        .first()
    )

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Obligation with ID "
                f"{obligation_id} not found"
            )
        )

    return obligation


# ============================================================
# 6. GET - Get Obligations for a Contract
# ============================================================

@router.get(
    "/contract/{contract_id}",
    response_model=list[ObligationResponse],
    status_code=status.HTTP_200_OK
)
def get_contract_obligations(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check whether contract exists
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Contract with ID "
                f"{contract_id} not found"
            )
        )

    return (
        db.query(Obligation)
        .filter(Obligation.contract_id == contract_id)
        .all()
    )


# ============================================================
# 7. PUT - Update Obligation
# ============================================================

@router.put(
    "/{obligation_id}",
    response_model=ObligationResponse,
    status_code=status.HTTP_200_OK
)
def update_obligation(
    obligation_id: int,
    obligation_data: ObligationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.MANAGE_OBLIGATIONS)
    )
):
    obligation = (
        db.query(Obligation)
        .filter(Obligation.id == obligation_id)
        .first()
    )

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Obligation with ID "
                f"{obligation_id} not found"
            )
        )

    # Update only fields provided by the client
    if obligation_data.title is not None:
        obligation.title = obligation_data.title

    if obligation_data.description is not None:
        obligation.description = obligation_data.description

    if obligation_data.obligation_type is not None:
        obligation.obligation_type = obligation_data.obligation_type

    if obligation_data.due_date is not None:
        obligation.due_date = obligation_data.due_date

    if obligation_data.assigned_to is not None:

        assigned_user = (
            db.query(User)
            .filter(User.id == obligation_data.assigned_to)
            .first()
        )

        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"User with ID "
                    f"{obligation_data.assigned_to} not found"
                )
            )

        obligation.assigned_to = obligation_data.assigned_to

    db.commit()
    db.refresh(obligation)

    return obligation


# ============================================================
# 8. PATCH - Update Obligation Status
# ============================================================

@router.patch(
    "/{obligation_id}/status",
    response_model=ObligationResponse,
    status_code=status.HTTP_200_OK
)
def update_obligation_status(
    obligation_id: int,
    status_data: ObligationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obligation = (
        db.query(Obligation)
        .filter(Obligation.id == obligation_id)
        .first()
    )

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Obligation with ID "
                f"{obligation_id} not found"
            )
        )

    current_status = obligation.status
    new_status = status_data.status

    # Valid obligation statuses
    valid_statuses = {
        "Pending",
        "In Progress",
        "Completed",
        "Delayed",
        "Overdue",
    }

    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid obligation status: {new_status}"
        )

    # Allowed workflow transitions
    allowed_transitions = {
        "Pending": {"In Progress"},
        "In Progress": {"Completed", "Delayed"},
        "Delayed": {"In Progress", "Completed"},
        "Completed": set(),
        "Overdue": {"In Progress", "Completed"},
    }

    if new_status not in allowed_transitions.get(
        current_status,
        set()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status transition: "
                f"{current_status} -> {new_status}"
            )
        )

    obligation.status = new_status

    if new_status == "In Progress":
        obligation.progress = 50

    elif new_status == "Completed":
        obligation.progress = 100
        obligation.completion_date = date.today()

    elif new_status == "Delayed":
        obligation.progress = 50

    db.commit()
    db.refresh(obligation)

    return obligation


# ============================================================
# 9. POST - Complete Obligation
# ============================================================

@router.post(
    "/{obligation_id}/complete",
    response_model=ObligationResponse,
    status_code=status.HTTP_200_OK
)
def complete_obligation(
    obligation_id: int,
    completion_data: ObligationComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obligation = (
        db.query(Obligation)
        .filter(Obligation.id == obligation_id)
        .first()
    )

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Obligation with ID "
                f"{obligation_id} not found"
            )
        )

    if obligation.status == "Completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Obligation is already completed"
        )

    if obligation.status not in {
        "Pending",
        "In Progress",
        "Delayed",
        "Overdue",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Obligation cannot be completed "
                f"from status {obligation.status}"
            )
        )

    obligation.status = "Completed"
    obligation.progress = 100
    obligation.completion_date = date.today()

    db.commit()
    db.refresh(obligation)

    return obligation