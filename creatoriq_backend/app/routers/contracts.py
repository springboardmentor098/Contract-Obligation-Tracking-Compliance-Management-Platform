from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.user import User

from app.schemas.contract import (
    ContractCreate,
    ContractUpdate,
    ContractStatusUpdate,
    ContractAssignment,
    ContractResponse,
)

from app.core.dependencies import (
    get_current_user,
    require_permission,
)

from app.schemas.permissions import Permission


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)


# ============================================================
# 1. POST - Create Contract
# ============================================================

@router.post(
    "",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED
)
def create_contract(
    contract_data: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if contract number already exists
    existing_contract = (
        db.query(Contract)
        .filter(
            Contract.contract_number == contract_data.contract_number
        )
        .first()
    )

    if existing_contract:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract number already exists"
        )

    contract = Contract(
        title=contract_data.title,
        contract_number=contract_data.contract_number,
        category=contract_data.category,
        description=contract_data.description,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        status="Draft",

        # Automatically get user information from JWT
        created_by=current_user.id,
        assigned_to=current_user.id
    )

    db.add(contract)
    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# 2. GET - Get All Contracts
# ============================================================

@router.get(
    "",
    response_model=list[ContractResponse],
    status_code=status.HTTP_200_OK
)
def get_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Contract).all()


# ============================================================
# 3. GET - Get Contract by ID
# ============================================================

@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def get_contract_by_id(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found"
        )

    return contract


# ============================================================
# 4. PUT - Update Contract
# ============================================================

@router.put(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.MANAGE_CONTRACTS)
    )
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found"
        )

    update_data = contract_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(contract, field, value)

    contract.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# 5. PATCH - Update Contract Status
# ============================================================

@router.patch(
    "/{contract_id}/status",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def update_contract_status(
    contract_id: int,
    status_data: ContractStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.MANAGE_CONTRACTS)
    )
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found"
        )

    allowed_statuses = {
        "Draft",
        "Under Review",
        "Approved",
        "Active",
        "Expired",
        "Terminated"
    }

    if status_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid contract status"
        )

    allowed_transitions = {
        "Draft": {"Under Review"},
        "Under Review": {"Approved"},
        "Approved": {"Active"},
        "Active": {"Expired", "Terminated"},
        "Expired": set(),
        "Terminated": set()
    }

    current_status = contract.status
    new_status = status_data.status

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

    contract.status = new_status
    contract.updated_at = datetime.utcnow()

    if new_status == "Under Review":
        contract.reviewed_at = datetime.utcnow()

    if new_status == "Approved":
        contract.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# 6. POST - Submit Contract for Review
# ============================================================

@router.post(
    "/{contract_id}/submit-review",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def submit_contract_for_review(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.MANAGE_CONTRACTS)
    )
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found"
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
    contract.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# 7. POST - Approve Contract
# ============================================================

@router.post(
    "/{contract_id}/approve",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def approve_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.MANAGE_CONTRACTS)
    )
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found"
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
    contract.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# 8. POST - Activate Contract
# ============================================================

@router.post(
    "/{contract_id}/activate",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def activate_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.MANAGE_CONTRACTS)
    )
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found"
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
    contract.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# 9. PATCH - Assign Contract
# ============================================================

@router.patch(
    "/{contract_id}/assignment",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def assign_contract(
    contract_id: int,
    assignment_data: ContractAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.MANAGE_CONTRACTS)
    )
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found"
        )

    assigned_user = (
        db.query(User)
        .filter(
            User.id == assignment_data.assigned_to,
            User.is_active == True
        )
        .first()
    )

    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found or inactive"
        )

    contract.assigned_to = assigned_user.id
    contract.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract