from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.user import User
from app.models.renewal import Renewal
from app.schemas.renewal import RenewalResponse

from app.schemas.contract import (
    ContractCreate,
    ContractUpdate,
    ContractStatusUpdate,
    ContractAssignment,
    ContractResponse,
)

from app.schemas.permissions import Permission
from app.core.dependencies import (
    get_current_user,
    require_permission,
)

from app.services.notification_service import (
    create_contract_approval_notification,
)


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
    status_code=status.HTTP_201_CREATED,
)
def create_contract(
    contract_data: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.MANAGE_CONTRACTS)
    ),
):
    # Check duplicate contract number
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
            detail="Contract number already exists",
        )

    contract = Contract(
        title=contract_data.title,
        contract_number=contract_data.contract_number,
        category=contract_data.category,
        description=contract_data.description,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,

        # New contracts always start as Draft
        status="Draft",

        # Authenticated user
        created_by=current_user.id,
        assigned_to=current_user.id,
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
    status_code=status.HTTP_200_OK,
)
def get_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Contract).all()


# ============================================================
# 3. PUT - Update Contract
# ============================================================

@router.put(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
)
def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.MANAGE_CONTRACTS)
    ),
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found",
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

    contract.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# 4. GET - Get Contract's Obligations
# ============================================================

@router.get(
    "/{contract_id}/obligations",
    status_code=status.HTTP_200_OK,
)
def get_contract_obligations(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
            detail=f"Contract with ID {contract_id} not found",
        )

    obligations = (
        db.query(Obligation)
        .filter(
            Obligation.contract_id == contract_id
        )
        .all()
    )

    return obligations


# ============================================================
# 5. PATCH - Change Contract Status
# ============================================================

@router.patch(
    "/{contract_id}/status",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
)
def update_contract_status(
    contract_id: int,
    status_data: ContractStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.MANAGE_CONTRACTS)
    ),
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found",
        )

    current_status = contract.status
    new_status = status_data.status

    # Valid contract workflow
    valid_transitions = {
        "Draft": ["Under Review"],
        "Under Review": ["Approved"],
        "Approved": ["Active"],
        "Active": ["Expired", "Terminated"],
        "Expired": [],
        "Terminated": [],
    }

    allowed_statuses = valid_transitions.get(
        current_status,
        []
    )

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status transition: "
                f"{current_status} -> {new_status}"
            ),
        )

    contract.status = new_status
    contract.updated_at = datetime.utcnow()

    # Workflow timestamps
    if new_status == "Under Review":
        contract.reviewed_at = datetime.utcnow()

    elif new_status == "Approved":
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
    status_code=status.HTTP_200_OK,
)
def submit_contract_for_review(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.MANAGE_CONTRACTS)
    ),
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found",
        )

    # Only Draft contracts can be submitted
    if contract.status != "Draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only Draft contracts can be "
                "submitted for review"
            ),
        )

    contract.status = "Under Review"
    contract.reviewed_at = datetime.utcnow()
    contract.updated_at = datetime.utcnow()

    # --------------------------------------------------------
    # Create approval notification for Legal Manager
    # --------------------------------------------------------

    legal_manager = (
        db.query(User)
        .filter(
            User.role == "Legal Manager",
            User.is_active == True
        )
        .first()
    )

    if legal_manager:
        create_contract_approval_notification(
            db=db,
            contract=contract,
            user_id=legal_manager.id,
        )

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# 7. POST - Approve Contract
# ============================================================

@router.post(
    "/{contract_id}/approve",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
)
def approve_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Only authorized roles can approve
    allowed_approval_roles = {
        "Administrator",
        "Legal Manager",
    }

    if current_user.role not in allowed_approval_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only Administrator or Legal Manager "
                "can approve contracts"
            ),
        )

    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found",
        )

    # Only Under Review contracts can be approved
    if contract.status != "Under Review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only contracts in Under Review status "
                "can be approved"
            ),
        )

    contract.status = "Approved"
    contract.approved_at = datetime.utcnow()
    contract.updated_at = datetime.utcnow()

    # --------------------------------------------------------
    # Create contract approved notification
    # --------------------------------------------------------

    if contract.assigned_to:
        notification = create_contract_approval_notification(
            db=db,
            contract=contract,
            user_id=contract.assigned_to,
        )

        notification.notification_type = "Contract Status"
        notification.title = "Contract Approved"
        notification.message = (
            f"Contract {contract.contract_number} "
            "has been approved."
        )

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# 8. POST - Activate Contract
# ============================================================

@router.post(
    "/{contract_id}/activate",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
)
def activate_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.MANAGE_CONTRACTS)
    ),
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found",
        )

    # Only Approved contracts can be activated
    if contract.status != "Approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only Approved contracts can be activated"
            ),
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
    status_code=status.HTTP_200_OK,
)
def assign_contract(
    contract_id: int,
    assignment_data: ContractAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.MANAGE_CONTRACTS)
    ),
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found",
        )

    # Check assigned user
    assigned_user = (
        db.query(User)
        .filter(
            User.id == assignment_data.assigned_to
        )
        .first()
    )

    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"User with ID "
                f"{assignment_data.assigned_to} not found"
            ),
        )

    if not assigned_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot assign contract to an inactive user",
        )

    contract.assigned_to = assignment_data.assigned_to
    contract.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# 10. GET - Get Contract By ID
# ============================================================

@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
)
def get_contract_by_id(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found",
        )

    return contract


# ============================================================
# 11. GET - Get Contract Renewals
# ============================================================

@router.get(
    "/{contract_id}/renewals",
    response_model=list[RenewalResponse],
    status_code=status.HTTP_200_OK
)
def get_contract_renewals(
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

    return (
        db.query(Renewal)
        .filter(Renewal.contract_id == contract_id)
        .all()
    )