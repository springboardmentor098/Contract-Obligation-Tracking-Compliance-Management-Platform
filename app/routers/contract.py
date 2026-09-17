from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.user import User
from app.schemas.contract import (
    ContractCreate,
    ContractUpdate,
    ContractResponse,
    ContractStatusUpdate,
    ContractAssignment,
)
from app.dependencies.authentication import get_current_user
from app.dependencies.authorization import require_roles


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)


# ============================================================
# CONTRACT WORKFLOW
# ============================================================

ALLOWED_STATUSES = {
    "Draft",
    "Under Review",
    "Approved",
    "Active",
    "Expired",
    "Terminated",
}


VALID_TRANSITIONS = {
    "Draft": ["Under Review"],
    "Under Review": ["Approved"],
    "Approved": ["Active"],
    "Active": ["Expired", "Terminated"],
}


# ============================================================
# CREATE CONTRACT
# Administrator, Legal Manager, Contract Manager
#
# New contracts always start with Draft status.
# ============================================================

@router.post(
    "",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED
)
def create_contract(
    contract_data: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Contract Manager"
        )
    )
):

    # Check duplicate contract number
    existing_contract = db.query(Contract).filter(
        Contract.contract_number == contract_data.contract_number
    ).first()

    if existing_contract:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract number already exists"
        )

    # Create contract
    contract = Contract(
        title=contract_data.title,
        contract_number=contract_data.contract_number,
        category=contract_data.category,
        description=contract_data.description,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,

        # Backend controls workflow status
        status="Draft",

        # Current logged-in user becomes creator
        created_by=current_user.id
    )

    db.add(contract)
    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# GET ALL CONTRACTS
# All authenticated roles
# ============================================================

@router.get(
    "",
    response_model=list[ContractResponse]
)
def get_contracts(
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

    return db.query(Contract).all()


# ============================================================
# GET CONTRACT BY ID
# All authenticated roles
# ============================================================

@router.get(
    "/{contract_id}",
    response_model=ContractResponse
)
def get_contract(
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

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found"
        )

    return contract


# ============================================================
# UPDATE CONTRACT
# Administrator, Legal Manager, Contract Manager
#
# Only contract information can be updated here.
# Status is NOT updated through this endpoint.
# ============================================================

@router.put(
    "/{contract_id}",
    response_model=ContractResponse
)
def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Contract Manager"
        )
    )
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found"
        )

    # Update only fields supplied by the user
    if contract_data.title is not None:
        contract.title = contract_data.title

    if contract_data.category is not None:
        contract.category = contract_data.category

    if contract_data.description is not None:
        contract.description = contract_data.description

    if contract_data.start_date is not None:
        contract.start_date = contract_data.start_date

    if contract_data.end_date is not None:
        contract.end_date = contract_data.end_date

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# UPDATE CONTRACT STATUS
# Administrator, Legal Manager, Contract Manager
#
# Only valid workflow transitions are allowed.
# ============================================================

@router.patch(
    "/{contract_id}/status",
    response_model=ContractResponse
)
def update_contract_status(
    contract_id: int,
    status_data: ContractStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Contract Manager"
        )
    )
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found"
        )

    new_status = status_data.status

    # Check whether status name is valid
    if new_status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid contract status: {new_status}"
        )

    # Get valid next statuses
    allowed_next_statuses = VALID_TRANSITIONS.get(
        contract.status,
        []
    )

    # Check workflow transition
    if new_status not in allowed_next_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status transition: "
                f"{contract.status} -> {new_status}"
            )
        )

    contract.status = new_status

    # Store review time
    if new_status == "Under Review":
        contract.reviewed_at = datetime.utcnow()

    # Store approval time
    if new_status == "Approved":
        contract.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# SUBMIT CONTRACT FOR REVIEW
#
# Draft -> Under Review
#
# Administrator, Legal Manager, Contract Manager
# ============================================================

@router.post(
    "/{contract_id}/submit-review",
    response_model=ContractResponse
)
def submit_contract_for_review(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Contract Manager"
        )
    )
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found"
        )

    # Only Draft contracts can be submitted
    if contract.status != "Draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only Draft contracts can be "
                "submitted for review"
            )
        )

    contract.status = "Under Review"
    contract.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# APPROVE CONTRACT
#
# Under Review -> Approved
#
# Only Administrator and Legal Manager
# ============================================================

@router.post(
    "/{contract_id}/approve",
    response_model=ContractResponse
)
def approve_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Administrator",
            "Legal Manager"
        )
    )
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found"
        )

    # Contract must be Under Review
    if contract.status != "Under Review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only contracts under review "
                "can be approved"
            )
        )

    contract.status = "Approved"
    contract.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# ACTIVATE CONTRACT
#
# Approved -> Active
#
# Administrator, Legal Manager, Contract Manager
# ============================================================

@router.post(
    "/{contract_id}/activate",
    response_model=ContractResponse
)
def activate_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Contract Manager"
        )
    )
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found"
        )

    # Contract must be Approved
    if contract.status != "Approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only approved contracts "
                "can be activated"
            )
        )

    contract.status = "Active"

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# ASSIGN CONTRACT
#
# Administrator, Legal Manager, Contract Manager
# ============================================================

@router.patch(
    "/{contract_id}/assign",
    response_model=ContractResponse
)
def assign_contract(
    contract_id: int,
    assignment: ContractAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Contract Manager"
        )
    )
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found"
        )

    # Check assigned user exists
    assigned_user = db.query(User).filter(
        User.id == assignment.assigned_to
    ).first()

    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"User {assignment.assigned_to} "
                "not found"
            )
        )

    contract.assigned_to = assigned_user.id

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# DELETE CONTRACT
# Administrator, Legal Manager, Contract Manager
# ============================================================

@router.delete(
    "/{contract_id}",
    status_code=status.HTTP_200_OK
)
def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Contract Manager"
        )
    )
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract {contract_id} not found"
        )

    db.delete(contract)
    db.commit()

    return {
        "message": f"Contract {contract_id} deleted successfully"
    }