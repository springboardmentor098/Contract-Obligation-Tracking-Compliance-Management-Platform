from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.roles import UserRole, normalize_role
from app.database.database import get_db
from app.models.contract import Contract
from app.models.user import User
from app.schemas.contract import (
    ContractAssign,
    ContractCreate,
    ContractResponse,
    ContractStatusUpdate,
    ContractUpdate,
    VALID_CONTRACT_STATUSES,
)

router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)

# Roles allowed to approve contracts
APPROVE_ALLOWED_ROLES = [
    UserRole.ADMINISTRATOR.value,
    UserRole.LEGAL_MANAGER.value,
    UserRole.COMPLIANCE_OFFICER.value,
    UserRole.CONTRACT_MANAGER.value,
    UserRole.DEPARTMENT_HEAD.value,
]

# Valid status transition mapping
VALID_TRANSITIONS = {
    "Draft": ["Under Review"],
    "Under Review": ["Approved", "Draft"],
    "Approved": ["Active", "Under Review"],
    "Active": ["Expired", "Terminated"],
    "Expired": [],
    "Terminated": []
}


def validate_status_transition(current_status: str, new_status: str):
    """Validate if target status transition is permitted by workflow rules."""
    if new_status not in VALID_CONTRACT_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{new_status}'. Supported statuses: {', '.join(VALID_CONTRACT_STATUSES)}."
        )
    
    if current_status == new_status:
        return

    allowed = VALID_TRANSITIONS.get(current_status, [])
    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from '{current_status}' to '{new_status}'. Allowed target status(es) from '{current_status}': {allowed if allowed else 'None'}."
        )


@router.post(
    "",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new contract",
    description="Creates a new contract in the repository and associates it with the authenticated user."
)
def create_contract(
    contract_in: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new contract in the database for the authenticated user."""
    # 1. Check if contract_number already exists
    existing_contract = db.query(Contract).filter(
        Contract.contract_number == contract_in.contract_number.strip()
    ).first()

    if existing_contract:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Contract number '{contract_in.contract_number}' already exists in the database. Please use an unused unique number like 'CNT-9001', 'CNT-9002', or 'CNT-2026-A'."
        )

    # 2. Extract user ID from authenticated JWT user
    raw_user_id = getattr(current_user, "user_id", None) or getattr(current_user, "id", None)
    db_user = None
    if raw_user_id:
        db_user = db.query(User).filter((User.user_id == raw_user_id) | (User.id == raw_user_id)).first()
    if not db_user and hasattr(current_user, "email") and current_user.email:
        db_user = db.query(User).filter(User.email == current_user.email).first()

    if db_user:
        user_id = getattr(db_user, "user_id", None) or getattr(db_user, "id", 1)
    else:
        first_user = db.query(User).first()
        user_id = getattr(first_user, "user_id", 1) if first_user else (raw_user_id or 1)

    assigned_to_id = contract_in.assigned_to if contract_in.assigned_to and contract_in.assigned_to != 0 else None
    if assigned_to_id:
        assigned_user = db.query(User).filter((User.user_id == assigned_to_id) | (User.id == assigned_to_id)).first()
        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid assigned user ID '{assigned_to_id}'. User with ID {assigned_to_id} does not exist in the database."
            )

    new_contract = Contract(
        title=contract_in.title.strip(),
        contract_number=contract_in.contract_number.strip(),
        category=contract_in.category.strip(),
        description=contract_in.description.strip() if contract_in.description else None,
        start_date=contract_in.start_date,
        end_date=contract_in.end_date,
        status=contract_in.status if contract_in.status else "Draft",
        created_by=user_id,
        assigned_to=assigned_to_id
    )

    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)

    return new_contract


@router.get(
    "",
    response_model=List[ContractResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve all contracts",
    description="Retrieves all contracts available in the repository for authenticated users."
)
def get_all_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all contracts available to the authenticated user."""
    contracts = db.query(Contract).all()
    return contracts


@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
    summary="Get contract by ID",
    description="Retrieves a single contract by its unique ID."
)
def get_contract_by_id(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific contract details by ID."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found."
        )

    return contract


@router.put(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Contract",
    description="Allows authorized users to update title, category, description, start_date, end_date, assigned_to."
)
def update_contract(
    contract_id: int,
    contract_in: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update contract information."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found."
        )

    if contract_in.title is not None:
        contract.title = contract_in.title.strip()
    if contract_in.category is not None:
        contract.category = contract_in.category.strip()
    if contract_in.description is not None:
        contract.description = contract_in.description.strip()
    if contract_in.start_date is not None:
        contract.start_date = contract_in.start_date
    if contract_in.end_date is not None:
        contract.end_date = contract_in.end_date
    if contract_in.assigned_to is not None:
        if contract_in.assigned_to == 0:
            contract.assigned_to = None
        else:
            assigned_user = db.query(User).filter((User.user_id == contract_in.assigned_to) | (User.id == contract_in.assigned_to)).first()
            if not assigned_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid assigned user ID '{contract_in.assigned_to}'. User with ID {contract_in.assigned_to} does not exist in the database."
                )
            contract.assigned_to = contract_in.assigned_to

    contract.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(contract)

    return contract


@router.patch(
    "/{contract_id}/status",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
    summary="Contract Status Management",
    description="Allows contract status to be changed according to the defined workflow rules."
)
def update_contract_status(
    contract_id: int,
    status_in: ContractStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Change contract status with workflow validation."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found."
        )

    target_status = status_in.status.strip()
    validate_status_transition(contract.status, target_status)

    contract.status = target_status
    if target_status == "Under Review":
        contract.reviewed_at = datetime.utcnow()
    elif target_status == "Approved":
        contract.approved_at = datetime.utcnow()

    contract.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(contract)

    return contract


@router.post(
    "/{contract_id}/submit-review",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit Contract for Review",
    description="Transitions contract from Draft to Under Review."
)
def submit_contract_for_review(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a Draft contract for review."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found."
        )

    if contract.status != "Draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot submit contract in '{contract.status}' status for review. Only contracts in 'Draft' status can be submitted for review."
        )

    contract.status = "Under Review"
    contract.reviewed_at = datetime.utcnow()
    contract.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(contract)

    return contract


@router.post(
    "/{contract_id}/approve",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve Contract",
    description="Transitions contract from Under Review to Approved for authorized roles."
)
def approve_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve contract under review (Role Restricted)."""
    user_role = normalize_role(getattr(current_user, "role", ""))
    if user_role not in APPROVE_ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Forbidden: User role '{current_user.role}' is not authorized to approve contracts. Allowed roles: Administrator, Legal Manager, Compliance Officer, Contract Manager, Department Head."
        )

    contract = db.query(Contract).filter(Contract.id == contract_id).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found."
        )

    if contract.status != "Under Review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve contract in '{contract.status}' status. Only contracts under review can be approved."
        )

    contract.status = "Approved"
    contract.approved_at = datetime.utcnow()
    contract.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(contract)

    return contract


@router.post(
    "/{contract_id}/activate",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate Contract",
    description="Transitions contract from Approved to Active."
)
def activate_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Activate an approved contract."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found."
        )

    if contract.status != "Approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot activate contract in '{contract.status}' status. Only approved contracts can be activated."
        )

    contract.status = "Active"
    contract.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(contract)

    return contract


@router.patch(
    "/{contract_id}/assign",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
    summary="Contract Assignment",
    description="Assigns a contract to a responsible user."
)
def assign_contract(
    contract_id: int,
    assign_in: ContractAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign contract to a responsible user."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found."
        )

    assigned_user = db.query(User).filter((User.user_id == assign_in.assigned_to) | (User.id == assign_in.assigned_to)).first()
    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assigned user with ID {assign_in.assigned_to} not found."
        )

    contract.assigned_to = assign_in.assigned_to
    contract.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(contract)

    return contract
