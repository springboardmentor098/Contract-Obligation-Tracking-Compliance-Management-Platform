from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.user import User
from app.schemas.contract_schema import (
    ContractCreate,
    ContractUpdate,
    ContractStatusUpdate,
    ContractAssignment,
    ContractResponse,
)
from app.middleware.auth import require_roles


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)


# ============================================================
# CREATE CONTRACT
# Administrator, Legal Manager, Contract Manager
# ============================================================

@router.post(
    "",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contract(
    contract_data: ContractCreate,
    current_user: dict = Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Contract Manager"
        )
    ),
    db: Session = Depends(get_db)
):

    # Check duplicate contract number
    existing_contract = db.query(Contract).filter(
        Contract.contract_number == contract_data.contract_number
    ).first()

    if existing_contract:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contract number already exists"
        )

    user_id = current_user["user_id"]

    contract = Contract(
        title=contract_data.title,
        contract_number=contract_data.contract_number,
        category=contract_data.category,
        description=contract_data.description,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        status="Draft",
        created_by=user_id
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
    response_model=list[ContractResponse],
    status_code=status.HTTP_200_OK,
)
def get_contracts(
    current_user: dict = Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Compliance Officer",
            "Contract Manager",
            "Department Head",
            "Employee"
        )
    ),
    db: Session = Depends(get_db)
):

    contracts = db.query(Contract).all()

    return contracts


# ============================================================
# GET CONTRACT BY ID
# All authenticated roles
# ============================================================

@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
)
def get_contract(
    contract_id: int,
    current_user: dict = Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Compliance Officer",
            "Contract Manager",
            "Department Head",
            "Employee"
        )
    ),
    db: Session = Depends(get_db)
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return contract


# ============================================================
# UPDATE CONTRACT
# Administrator, Legal Manager, Contract Manager
# ============================================================

@router.put(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
)
def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    current_user: dict = Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Contract Manager"
        )
    ),
    db: Session = Depends(get_db)
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Check duplicate contract number
    existing_contract = db.query(Contract).filter(
        Contract.contract_number == contract_data.contract_number,
        Contract.id != contract_id
    ).first()

    if existing_contract:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contract number already exists"
        )

    contract.title = contract_data.title
    contract.contract_number = contract_data.contract_number
    contract.category = contract_data.category
    contract.description = contract_data.description
    contract.start_date = contract_data.start_date
    contract.end_date = contract_data.end_date

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# UPDATE STATUS
#
# This endpoint allows controlled workflow transitions.
# ============================================================

@router.patch(
    "/{contract_id}/status",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
)
def update_contract_status(
    contract_id: int,
    status_data: ContractStatusUpdate,
    current_user: dict = Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Contract Manager"
        )
    ),
    db: Session = Depends(get_db)
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    current_status = contract.status
    new_status = status_data.status

    # Allowed workflow transitions
    allowed_transitions = {
        "Draft": ["Under Review"],
        "Under Review": ["Approved"],
        "Approved": ["Active"],
        "Active": ["Expired", "Terminated"],
        "Expired": [],
        "Terminated": []
    }

    if new_status not in allowed_transitions.get(current_status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status transition: "
                f"{current_status} -> {new_status}"
            )
        )

    contract.status = new_status

    if new_status == "Under Review":
        contract.reviewed_at = datetime.utcnow()

    elif new_status == "Approved":
        contract.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# SUBMIT CONTRACT FOR REVIEW
#
# Draft -> Under Review
# ============================================================

@router.post(
    "/{contract_id}/submit-review",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
)
def submit_for_review(
    contract_id: int,
    current_user: dict = Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Contract Manager"
        )
    ),
    db: Session = Depends(get_db)
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if contract.status != "Draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Contract cannot be submitted for review "
                f"from status '{contract.status}'"
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
# Only Administrator and Legal Manager can approve.
# ============================================================

@router.post(
    "/{contract_id}/approve",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
)
def approve_contract(
    contract_id: int,
    current_user: dict = Depends(
        require_roles(
            "Administrator",
            "Legal Manager"
        )
    ),
    db: Session = Depends(get_db)
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if contract.status != "Under Review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Contract cannot be approved "
                f"from status '{contract.status}'"
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
# ============================================================

@router.post(
    "/{contract_id}/activate",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
)
def activate_contract(
    contract_id: int,
    current_user: dict = Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Contract Manager"
        )
    ),
    db: Session = Depends(get_db)
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if contract.status != "Approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Contract cannot be activated "
                f"from status '{contract.status}'"
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
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
)
def assign_contract(
    contract_id: int,
    assignment_data: ContractAssignment,
    current_user: dict = Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Contract Manager"
        )
    ),
    db: Session = Depends(get_db)
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    assigned_user = db.query(User).filter(
        User.id == assignment_data.assigned_to,
        User.is_active == True
    ).first()

    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found or inactive"
        )

    contract.assigned_to = assignment_data.assigned_to

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# DELETE CONTRACT
# Administrator, Contract Manager
# ============================================================

@router.delete(
    "/{contract_id}",
    status_code=status.HTTP_200_OK,
)
def delete_contract(
    contract_id: int,
    current_user: dict = Depends(
        require_roles(
            "Administrator",
            "Contract Manager"
        )
    ),
    db: Session = Depends(get_db)
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    db.delete(contract)
    db.commit()

    return {
        "message": "Contract deleted successfully"
    }