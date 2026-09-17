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

from app.dependencies.authorization import require_roles


router = APIRouter(
    prefix="/obligations",
    tags=["Obligations"]
)


# =========================================================
# CONSTANTS
# =========================================================

ALLOWED_OBLIGATION_TYPES = {
    "Payment Obligation",
    "Delivery Commitment",
    "Reporting Requirement",
    "Renewal Condition",
    "Service Level Agreement",
    "Legal Compliance Requirement",
}


ALLOWED_STATUSES = {
    "Pending",
    "In Progress",
    "Completed",
    "Delayed",
    "Overdue",
}


VALID_STATUS_TRANSITIONS = {
    "Pending": [
        "In Progress",
        "Delayed",
    ],
    "In Progress": [
        "Completed",
        "Delayed",
    ],
    "Delayed": [
        "In Progress",
        "Completed",
    ],
    "Overdue": [
        "In Progress",
        "Completed",
    ],
    "Completed": []
}


# =========================================================
# HELPER FUNCTION
# =========================================================

def get_obligation_or_404(
    obligation_id: int,
    db: Session
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Obligation {obligation_id} not found"
        )

    return obligation


# =========================================================
# CREATE OBLIGATION
#
# Administrator
# Legal Manager
# Compliance Officer
# Contract Manager
#
# New obligation always starts as Pending.
# =========================================================

@router.post(
    "",
    response_model=ObligationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_obligation(
    data: ObligationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Compliance Officer",
            "Contract Manager"
        )
    )
):

    # -----------------------------------------------------
    # Check contract exists
    # -----------------------------------------------------

    contract = db.query(Contract).filter(
        Contract.id == data.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {data.contract_id} not found"
        )

    # -----------------------------------------------------
    # Check assigned user exists
    # -----------------------------------------------------

    assigned_user = db.query(User).filter(
        User.id == data.assigned_to
    ).first()

    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {data.assigned_to} not found"
        )

    # -----------------------------------------------------
    # Validate obligation type
    # -----------------------------------------------------

    if data.obligation_type not in ALLOWED_OBLIGATION_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid obligation type: "
                f"{data.obligation_type}. "
                f"Allowed types: "
                f"{', '.join(sorted(ALLOWED_OBLIGATION_TYPES))}"
            )
        )

    # -----------------------------------------------------
    # Create obligation
    # -----------------------------------------------------

    obligation = Obligation(
        contract_id=data.contract_id,
        title=data.title,
        description=data.description,
        obligation_type=data.obligation_type,
        due_date=data.due_date,
        assigned_to=data.assigned_to,

        # Backend controls initial status
        status="Pending",

        # Completion date starts empty
        completion_date=None
    )

    db.add(obligation)
    db.commit()
    db.refresh(obligation)

    return obligation


# =========================================================
# GET ALL OBLIGATIONS
#
# All authenticated roles
# =========================================================

@router.get(
    "",
    response_model=list[ObligationResponse]
)
def get_obligations(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Compliance Officer",
            "Contract Manager",
            "Department Head",
            "Employee"
        )
    )
):

    obligations = db.query(Obligation).all()

    # -----------------------------------------------------
    # Automatically identify overdue obligations
    # -----------------------------------------------------

    today = date.today()

    changed = False

    for obligation in obligations:

        if (
            obligation.status in {
                "Pending",
                "In Progress",
                "Delayed"
            }
            and obligation.due_date < today
            and obligation.completion_date is None
        ):
            obligation.status = "Overdue"
            changed = True

    if changed:
        db.commit()

    return obligations


# =========================================================
# GET OBLIGATION BY ID
#
# All authenticated roles
# =========================================================

@router.get(
    "/{obligation_id}",
    response_model=ObligationResponse
)
def get_obligation(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Compliance Officer",
            "Contract Manager",
            "Department Head",
            "Employee"
        )
    )
):

    obligation = get_obligation_or_404(
        obligation_id,
        db
    )

    # -----------------------------------------------------
    # Check overdue status
    # -----------------------------------------------------

    if (
        obligation.status in {
            "Pending",
            "In Progress",
            "Delayed"
        }
        and obligation.due_date < date.today()
        and obligation.completion_date is None
    ):
        obligation.status = "Overdue"
        db.commit()
        db.refresh(obligation)

    return obligation


# =========================================================
# GET OBLIGATIONS FOR A CONTRACT
#
# GET /contracts/{contract_id}/obligations
#
# All authenticated roles
# =========================================================

@router.get(
    "/contracts/{contract_id}/obligations",
    response_model=list[ObligationResponse]
)
def get_contract_obligations(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Compliance Officer",
            "Contract Manager",
            "Department Head",
            "Employee"
        )
    )
):

    # -----------------------------------------------------
    # Check contract exists
    # -----------------------------------------------------

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found"
        )

    obligations = db.query(Obligation).filter(
        Obligation.contract_id == contract_id
    ).all()

    # -----------------------------------------------------
    # Detect overdue obligations
    # -----------------------------------------------------

    today = date.today()
    changed = False

    for obligation in obligations:

        if (
            obligation.status in {
                "Pending",
                "In Progress",
                "Delayed"
            }
            and obligation.due_date < today
            and obligation.completion_date is None
        ):
            obligation.status = "Overdue"
            changed = True

    if changed:
        db.commit()

    return obligations


# =========================================================
# UPDATE OBLIGATION
#
# Administrator
# Compliance Officer
# Contract Manager
#
# Allowed:
# - title
# - description
# - obligation type
# - due date
# - assigned user
#
# Status and completion date cannot be changed here.
# =========================================================

@router.put(
    "/{obligation_id}",
    response_model=ObligationResponse
)
def update_obligation(
    obligation_id: int,
    data: ObligationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Administrator",
            "Compliance Officer",
            "Contract Manager"
        )
    )
):

    obligation = get_obligation_or_404(
        obligation_id,
        db
    )

    update_data = data.model_dump(
        exclude_unset=True
    )

    # -----------------------------------------------------
    # Validate obligation type
    # -----------------------------------------------------

    if (
        "obligation_type" in update_data
        and update_data["obligation_type"]
        not in ALLOWED_OBLIGATION_TYPES
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid obligation type: "
                f"{update_data['obligation_type']}"
            )
        )

    # -----------------------------------------------------
    # Validate assigned user
    # -----------------------------------------------------

    if "assigned_to" in update_data:

        assigned_user = db.query(User).filter(
            User.id == update_data["assigned_to"]
        ).first()

        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"User "
                    f"{update_data['assigned_to']} "
                    f"not found"
                )
            )

    # -----------------------------------------------------
    # Update allowed fields
    # -----------------------------------------------------

    for key, value in update_data.items():
        setattr(
            obligation,
            key,
            value
        )

    db.commit()
    db.refresh(obligation)

    return obligation


# =========================================================
# UPDATE OBLIGATION STATUS
#
# PATCH /obligations/{obligation_id}/status
#
# Administrator
# Compliance Officer
# Contract Manager
# Employee
# =========================================================

@router.patch(
    "/{obligation_id}/status",
    response_model=ObligationResponse
)
def update_obligation_status(
    obligation_id: int,
    data: ObligationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Administrator",
            "Compliance Officer",
            "Contract Manager",
            "Employee"
        )
    )
):

    obligation = get_obligation_or_404(
        obligation_id,
        db
    )

    new_status = data.status

    # -----------------------------------------------------
    # Validate status name
    # -----------------------------------------------------

    if new_status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid obligation status: {new_status}"
        )

    # -----------------------------------------------------
    # Prevent changing completed obligation
    # -----------------------------------------------------

    if obligation.status == "Completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completed obligations cannot be changed"
        )

    # -----------------------------------------------------
    # Validate transition
    # -----------------------------------------------------

    allowed_next_statuses = VALID_STATUS_TRANSITIONS.get(
        obligation.status,
        []
    )

    if new_status not in allowed_next_statuses:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status transition: "
                f"{obligation.status} -> {new_status}"
            )
        )

    # -----------------------------------------------------
    # Update status
    # -----------------------------------------------------

    obligation.status = new_status

    db.commit()
    db.refresh(obligation)

    return obligation


# =========================================================
# COMPLETE OBLIGATION
#
# POST /obligations/{obligation_id}/complete
#
# The backend determines completion date.
# =========================================================

@router.post(
    "/{obligation_id}/complete",
    response_model=ObligationResponse
)
def complete_obligation(
    obligation_id: int,
    data: ObligationComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Administrator",
            "Compliance Officer",
            "Contract Manager",
            "Employee"
        )
    )
):

    obligation = get_obligation_or_404(
        obligation_id,
        db
    )

    # -----------------------------------------------------
    # Already completed
    # -----------------------------------------------------

    if obligation.status == "Completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Obligation is already completed"
        )

    # -----------------------------------------------------
    # Complete obligation
    # -----------------------------------------------------

    obligation.status = "Completed"
    obligation.completion_date = date.today()

    db.commit()
    db.refresh(obligation)

    return obligation