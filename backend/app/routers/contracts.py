from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.rbac import UserRole
from app.database.database import get_db
from app.models.contract import Contract
from app.models.user import User
from app.schemas.contract import (
    ContractAssignment,
    ContractCreate,
    ContractResponse,
    ContractStatusUpdate,
    ContractUpdate,
)


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"],
)


# ============================================================
# CONSTANTS
# ============================================================

VALID_STATUSES = {
    "Draft",
    "Under Review",
    "Approved",
    "Active",
}


ALLOWED_TRANSITIONS = {
    "Draft": {"Under Review"},
    "Under Review": {"Approved"},
    "Approved": {"Active"},
    "Active": set(),
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_contract_or_404(
    contract_id: UUID,
    db: Session,
) -> Contract:
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    return contract


def check_contract_access(
    contract: Contract,
    current_user: User,
) -> None:
    allowed_roles = {
        UserRole.ADMINISTRATOR.value,
        UserRole.LEGAL_MANAGER.value,
        UserRole.CONTRACT_MANAGER.value,
    }

    if current_user.role in allowed_roles:
        return

    if contract.created_by == current_user.id:
        return

    if contract.assigned_to == current_user.id:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this contract",
    )


def check_contract_management_permission(
    current_user: User,
) -> None:
    allowed_roles = {
        UserRole.ADMINISTRATOR.value,
        UserRole.LEGAL_MANAGER.value,
        UserRole.CONTRACT_MANAGER.value,
    }

    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage contracts",
        )


# ============================================================
# CREATE CONTRACT
# ============================================================

@router.post(
    "",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contract(
    contract_data: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_contract_management_permission(current_user)

    if contract_data.assigned_to:
        assignee = (
            db.query(User)
            .filter(
                User.id == contract_data.assigned_to,
                User.is_active.is_(True),
            )
            .first()
        )

        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found or inactive",
            )

    contract = Contract(
        title=contract_data.title,
        contract_number=contract_data.contract_number,
        category=contract_data.category,
        description=contract_data.description,
        counterparty_name=contract_data.counterparty_name,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        contract_value=contract_data.contract_value,
        currency=contract_data.currency,
        assigned_to=contract_data.assigned_to,
        status="Draft",
        created_by=current_user.id,
    )

    db.add(contract)

    try:
        db.commit()
        db.refresh(contract)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contract number already exists",
        )

    return contract


# ============================================================
# GET ALL CONTRACTS
# ============================================================

@router.get(
    "",
    response_model=list[ContractResponse],
)
def get_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contracts = (
        db.query(Contract)
        .filter(
            (Contract.created_by == current_user.id)
            | (Contract.assigned_to == current_user.id)
        )
        .all()
    )

    if current_user.role == UserRole.ADMINISTRATOR.value:
        contracts = db.query(Contract).all()

    return contracts


# ============================================================
# GET CONTRACT BY ID
# ============================================================

@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
)
def get_contract(
    contract_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contract = get_contract_or_404(contract_id, db)

    check_contract_access(contract, current_user)

    return contract


# ============================================================
# UPDATE CONTRACT
# ============================================================

@router.put(
    "/{contract_id}",
    response_model=ContractResponse,
)
def update_contract(
    contract_id: UUID,
    contract_data: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_contract_management_permission(current_user)

    contract = get_contract_or_404(contract_id, db)

    if contract.status == "Active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active contracts cannot be updated",
        )

    if contract_data.assigned_to:
        assignee = (
            db.query(User)
            .filter(
                User.id == contract_data.assigned_to,
                User.is_active.is_(True),
            )
            .first()
        )

        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found or inactive",
            )

    update_data = contract_data.model_dump(
        exclude_unset=True,
        exclude_none=False,
    )

    # Status must be changed through the dedicated status endpoint.
    update_data.pop("status", None)

    for field, value in update_data.items():
        setattr(contract, field, value)

    try:
        db.commit()
        db.refresh(contract)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contract update violates a database constraint",
        )

    return contract


# ============================================================
# ASSIGN CONTRACT
# ============================================================

@router.patch(
    "/{contract_id}/assign",
    response_model=ContractResponse,
)
def assign_contract(
    contract_id: UUID,
    assignment: ContractAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_contract_management_permission(current_user)

    contract = get_contract_or_404(contract_id, db)

    assignee = (
        db.query(User)
        .filter(
            User.id == assignment.assigned_to,
            User.is_active.is_(True),
        )
        .first()
    )

    if not assignee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found or inactive",
        )

    contract.assigned_to = assignee.id

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# UPDATE CONTRACT STATUS
# ============================================================

@router.patch(
    "/{contract_id}/status",
    response_model=ContractResponse,
)
def update_contract_status(
    contract_id: UUID,
    status_data: ContractStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_contract_management_permission(current_user)

    contract = get_contract_or_404(contract_id, db)

    new_status = status_data.status

    if new_status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid status. Allowed statuses: "
                "Draft, Under Review, Approved, Active"
            ),
        )

    current_status = contract.status

    if new_status == current_status:
        return contract

    allowed_next_statuses = ALLOWED_TRANSITIONS.get(
        current_status,
        set(),
    )

    if new_status not in allowed_next_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status transition: "
                f"{current_status} -> {new_status}"
            ),
        )

    contract.status = new_status

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# SUBMIT CONTRACT FOR REVIEW
# ============================================================

@router.post(
    "/{contract_id}/submit-review",
    response_model=ContractResponse,
)
def submit_contract_for_review(
    contract_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_contract_management_permission(current_user)

    contract = get_contract_or_404(contract_id, db)

    if contract.status != "Draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Draft contracts can be submitted for review",
        )

    contract.status = "Under Review"

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# APPROVE CONTRACT
# ============================================================

@router.post(
    "/{contract_id}/approve",
    response_model=ContractResponse,
)
def approve_contract(
    contract_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed_roles = {
        UserRole.ADMINISTRATOR.value,
        UserRole.LEGAL_MANAGER.value,
    }

    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrator or Legal Manager can approve contracts",
        )

    contract = get_contract_or_404(contract_id, db)

    if contract.status != "Under Review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only contracts under review can be approved",
        )

    contract.status = "Approved"

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# ACTIVATE CONTRACT
# ============================================================

@router.post(
    "/{contract_id}/activate",
    response_model=ContractResponse,
)
def activate_contract(
    contract_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_contract_management_permission(current_user)

    contract = get_contract_or_404(contract_id, db)

    if contract.status != "Approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only approved contracts can be activated",
        )

    contract.status = "Active"

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# DELETE CONTRACT
# ============================================================

@router.delete(
    "/{contract_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_contract(
    contract_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.ADMINISTRATOR.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrator can delete contracts",
        )

    contract = get_contract_or_404(contract_id, db)

    db.delete(contract)
    db.commit()

    return None