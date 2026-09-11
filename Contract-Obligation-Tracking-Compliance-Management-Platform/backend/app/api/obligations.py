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
    ObligationStatus,
)
from app.core.security import get_current_user


# ============================================================
# Routers
# ============================================================

router = APIRouter(
    prefix="/obligations",
    tags=["Obligations"]
)

contract_obligations_router = APIRouter(
    prefix="/contracts",
    tags=["Obligations"]
)


# ============================================================
# Helper Functions
# ============================================================

def get_obligation_or_404(
    obligation_id: int,
    db: Session
) -> Obligation:
    """
    Get an obligation by ID or return 404.
    """

    obligation = (
        db.query(Obligation)
        .filter(
            Obligation.id == obligation_id
        )
        .first()
    )

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found"
        )

    return obligation


def get_contract_or_404(
    contract_id: int,
    db: Session
) -> Contract:
    """
    Get a contract by ID or return 404.
    """

    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id
        )
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return contract


def get_user_or_404(
    user_id: int,
    db: Session
) -> User:
    """
    Get a user by ID or return 404.
    """

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )

    return user


# ============================================================
# Overdue Detection
# ============================================================

def is_obligation_overdue(
    obligation: Obligation
) -> bool:
    """
    Determine whether an obligation is overdue.

    An obligation is overdue when:
    - Its due date has passed
    - It has not been completed
    """

    if obligation.status == "Completed":
        return False

    if obligation.due_date is None:
        return False

    return obligation.due_date < date.today()


def apply_overdue_status(
    obligation: Obligation
) -> bool:
    """
    Apply Overdue status when an obligation is overdue.

    Returns True if the status was changed.
    """

    if is_obligation_overdue(obligation):

        if obligation.status != "Overdue":
            obligation.status = "Overdue"
            return True

    return False


# ============================================================
# Status Transition Validation
# ============================================================

ALLOWED_STATUS_TRANSITIONS = {
    "Pending": {
        "In Progress",
        "Delayed",
        "Overdue"
    },

    "In Progress": {
        "Completed",
        "Delayed",
        "Overdue"
    },

    "Delayed": {
        "In Progress",
        "Completed",
        "Overdue"
    },

    "Overdue": {
        "In Progress",
        "Completed"
    },

    "Completed": set()
}


def validate_status_transition(
    current_status: str,
    new_status: ObligationStatus
) -> None:
    """
    Validate whether a requested status transition is allowed.
    """

    allowed_statuses = ALLOWED_STATUS_TRANSITIONS.get(
        current_status,
        set()
    )

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status transition: "
                f"{current_status} → {new_status}"
            )
        )


# ============================================================
# Authorization Helpers
# ============================================================

MANAGER_ROLES = {
    "Administrator",
    "Legal Manager",
    "Compliance Officer",
    "Contract Manager",
    "Department Head",
}


def is_manager(current_user: User) -> bool:
    """
    Check whether the current user has a management role.
    """

    return current_user.role in MANAGER_ROLES


def can_modify_obligation(
    obligation: Obligation,
    current_user: User
) -> bool:
    """
    Determine whether a user can modify an obligation.

    Managers can modify obligations.

    The user assigned to an obligation can also
    update its progress/status.
    """

    if is_manager(current_user):
        return True

    if obligation.assigned_to == current_user.id:
        return True

    return False


# ============================================================
# API 1 — Create Obligation
# ============================================================

@router.post(
    "",
    response_model=ObligationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_obligation(
    obligation_data: ObligationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new obligation for an existing contract.
    """

    # --------------------------------------------------------
    # Verify Contract
    # --------------------------------------------------------

    contract = get_contract_or_404(
        obligation_data.contract_id,
        db
    )

    # --------------------------------------------------------
    # Verify Assigned User
    # --------------------------------------------------------

    if obligation_data.assigned_to is not None:

        assigned_user = get_user_or_404(
            obligation_data.assigned_to,
            db
        )

        if not assigned_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned user account is inactive"
            )

    # --------------------------------------------------------
    # Authorization
    # --------------------------------------------------------

    if not is_manager(current_user):

        if contract.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to create an obligation for this contract"
                )
            )

    # --------------------------------------------------------
    # Create Obligation
    # --------------------------------------------------------

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


# ============================================================
# API 2 — Get All Obligations
# ============================================================

@router.get(
    "",
    response_model=list[ObligationResponse]
)
def get_obligations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return obligations according to authorization rules.
    """

    if is_manager(current_user):

        obligations = (
            db.query(Obligation)
            .order_by(Obligation.id)
            .all()
        )

    else:

        obligations = (
            db.query(Obligation)
            .filter(
                Obligation.assigned_to == current_user.id
            )
            .order_by(Obligation.id)
            .all()
        )

    # --------------------------------------------------------
    # Apply overdue detection
    # --------------------------------------------------------

    changed = False

    for obligation in obligations:

        if apply_overdue_status(obligation):
            changed = True

    if changed:

        db.commit()

        for obligation in obligations:
            db.refresh(obligation)

    return obligations


# ============================================================
# API 3 — Get Obligation by ID
# ============================================================

@router.get(
    "/{obligation_id}",
    response_model=ObligationResponse
)
def get_obligation(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return a specific obligation.
    """

    obligation = get_obligation_or_404(
        obligation_id,
        db
    )

    # --------------------------------------------------------
    # Authorization
    # --------------------------------------------------------

    if not is_manager(current_user):

        if obligation.assigned_to != current_user.id:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to view this obligation"
                )
            )

    # --------------------------------------------------------
    # Overdue Detection
    # --------------------------------------------------------

    if apply_overdue_status(obligation):

        db.commit()
        db.refresh(obligation)

    return obligation


# ============================================================
# API 4 — Get Obligations for a Contract
# ============================================================

@contract_obligations_router.get(
    "/{contract_id}/obligations",
    response_model=list[ObligationResponse]
)
def get_contract_obligations(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return all obligations belonging to a contract.
    """

    # --------------------------------------------------------
    # Verify Contract
    # --------------------------------------------------------

    contract = get_contract_or_404(
        contract_id,
        db
    )

    # --------------------------------------------------------
    # Authorization
    # --------------------------------------------------------

    if not is_manager(current_user):

        if contract.created_by != current_user.id:

            assigned_obligation_exists = (
                db.query(Obligation)
                .filter(
                    Obligation.contract_id == contract_id,
                    Obligation.assigned_to == current_user.id
                )
                .first()
            )

            if not assigned_obligation_exists:

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "You do not have permission "
                        "to view these obligations"
                    )
                )

    # --------------------------------------------------------
    # Get Obligations
    # --------------------------------------------------------

    if is_manager(current_user):

        obligations = (
            db.query(Obligation)
            .filter(
                Obligation.contract_id == contract_id
            )
            .order_by(Obligation.id)
            .all()
        )

    elif contract.created_by == current_user.id:

        obligations = (
            db.query(Obligation)
            .filter(
                Obligation.contract_id == contract_id
            )
            .order_by(Obligation.id)
            .all()
        )

    else:

        obligations = (
            db.query(Obligation)
            .filter(
                Obligation.contract_id == contract_id,
                Obligation.assigned_to == current_user.id
            )
            .order_by(Obligation.id)
            .all()
        )

    # --------------------------------------------------------
    # Apply overdue detection
    # --------------------------------------------------------

    changed = False

    for obligation in obligations:

        if apply_overdue_status(obligation):
            changed = True

    if changed:

        db.commit()

        for obligation in obligations:
            db.refresh(obligation)

    return obligations


# ============================================================
# API 5 — Update Obligation
# ============================================================

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
    """
    Update obligation information.
    """

    obligation = get_obligation_or_404(
        obligation_id,
        db
    )

    # --------------------------------------------------------
    # Authorization
    # --------------------------------------------------------

    if not can_modify_obligation(
        obligation,
        current_user
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to update this obligation"
            )
        )

    # --------------------------------------------------------
    # Assigned User Validation
    # --------------------------------------------------------

    if obligation_data.assigned_to is not None:

        assigned_user = get_user_or_404(
            obligation_data.assigned_to,
            db
        )

        if not assigned_user.is_active:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned user account is inactive"
            )

    # --------------------------------------------------------
    # Update Only Supplied Fields
    # --------------------------------------------------------

    update_data = obligation_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():

        setattr(
            obligation,
            field,
            value
        )

    db.commit()
    db.refresh(obligation)

    return obligation


# ============================================================
# API 6 — Update Obligation Status
# ============================================================

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
    """
    Update obligation status using the defined workflow.
    """

    obligation = get_obligation_or_404(
        obligation_id,
        db
    )

    # --------------------------------------------------------
    # Authorization
    # --------------------------------------------------------

    if not can_modify_obligation(
        obligation,
        current_user
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to update this obligation status"
            )
        )

    # --------------------------------------------------------
    # Detect Overdue
    # --------------------------------------------------------

    if is_obligation_overdue(obligation):

        if obligation.status != "Completed":
            obligation.status = "Overdue"

    current_status = obligation.status
    new_status = status_data.status

    # --------------------------------------------------------
    # Same Status
    # --------------------------------------------------------

    if current_status == new_status:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Obligation is already in "
                f"{current_status} status"
            )
        )

    # --------------------------------------------------------
    # Validate Transition
    # --------------------------------------------------------

    validate_status_transition(
        current_status,
        new_status
    )

    # --------------------------------------------------------
    # Completed Status
    # --------------------------------------------------------

    if new_status == "Completed":

        obligation.status = "Completed"
        obligation.completion_date = date.today()

    else:

        obligation.status = new_status

    db.commit()
    db.refresh(obligation)

    return obligation


# ============================================================
# API 7 — Complete Obligation
# ============================================================

@router.post(
    "/{obligation_id}/complete",
    response_model=ObligationResponse
)
def complete_obligation(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Complete an obligation.

    The completion date is determined automatically
    by the backend.
    """

    obligation = get_obligation_or_404(
        obligation_id,
        db
    )

    # --------------------------------------------------------
    # Authorization
    # --------------------------------------------------------

    if not can_modify_obligation(
        obligation,
        current_user
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to complete this obligation"
            )
        )

    # --------------------------------------------------------
    # Already Completed
    # --------------------------------------------------------

    if obligation.status == "Completed":

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Obligation is already completed"
        )

    # --------------------------------------------------------
    # Complete
    # --------------------------------------------------------

    obligation.status = "Completed"
    obligation.completion_date = date.today()

    db.commit()
    db.refresh(obligation)

    return obligation
