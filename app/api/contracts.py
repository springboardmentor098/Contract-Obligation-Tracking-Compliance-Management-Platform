from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models import contract
from app.models.contract import Contract
from app.models.user import User
from app.models.audit_log import AuditLog
from app.services.audit_service import create_audit_log
from app.schemas.contract_schema import (
    ContractCreate,
    ContractRead,
    ContractUpdate,
)
from app.core.dependencies import (
    get_current_user,
    require_permission,
)
from app.core.permissions import Permission, has_permission


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"],
)


def get_user_id(current_user: dict) -> int:
    return int(current_user["sub"])


# =========================================================
# CREATE CONTRACT
# =========================================================

@router.post(
    "",
    response_model=ContractRead,
    status_code=status.HTTP_201_CREATED,
)
def create_contract(
    contract_data: ContractCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.CREATE_CONTRACT)
    ),
):
    user_id = get_user_id(current_user)

    # Validate assigned user
    if contract_data.assigned_to is not None:
        assigned_user = (
            db.query(User)
            .filter(
                User.id == contract_data.assigned_to,
                User.is_active.is_(True),
            )
            .first()
        )

        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned user does not exist or is inactive",
            )

    # Prevent duplicate contract number
    existing = (
        db.query(Contract)
        .filter(
            Contract.contract_number == contract_data.contract_number
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contract number already exists",
        )

    contract = Contract(
        contract_number=contract_data.contract_number,
        title=contract_data.title,
        category=contract_data.category,
        description=contract_data.description,
        counterparty_name=contract_data.counterparty_name,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        created_by=user_id,
        assigned_to=contract_data.assigned_to,
        status="Draft",
    )

    db.add(contract)
    db.flush()

    create_audit_log(
        db=db,
        user_id=user_id,
        action="Created contract",
        entity_type="Contract",
        entity_id=contract.id,
        contract_id=contract.id,
        details=f"Contract {contract.contract_number} created",
    )

    db.commit()
    db.refresh(contract)

    return contract


# =========================================================
# LIST CONTRACTS
# =========================================================

@router.get(
    "",
    response_model=list[ContractRead],
)
def list_contracts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.READ_CONTRACT)
    ),
):
    return (
        db.query(Contract)
        .order_by(Contract.created_at.desc())
        .all()
    )


# =========================================================
# GET SINGLE CONTRACT
# =========================================================

@router.get(
    "/{contract_id}",
    response_model=ContractRead,
)
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.READ_CONTRACT)
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
            detail="Contract not found",
        )

    return contract


# =========================================================
# UPDATE CONTRACT
# =========================================================

@router.put(
    "/{contract_id}",
    response_model=ContractRead,
)
def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.UPDATE_CONTRACT)
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
            detail="Contract not found",
        )

    # Validate assigned user
    if contract_data.assigned_to is not None:
        assigned_user = (
            db.query(User)
            .filter(
                User.id == contract_data.assigned_to,
                User.is_active.is_(True),
            )
            .first()
        )

        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned user does not exist or is inactive",
            )

    update_data = contract_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(contract, field, value)

    contract.updated_at = datetime.now(timezone.utc)

    create_audit_log(
        db=db,
        user_id=get_user_id(current_user),
        action="Updated contract",
        entity_type="Contract",
        entity_id=contract.id,
        contract_id=contract.id,
        details=f"Contract {contract.contract_number} updated",
    )

    db.commit()
    db.refresh(contract)

    return contract


# =========================================================
# DELETE CONTRACT
# =========================================================

@router.delete(
    "/{contract_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.DELETE_CONTRACT)
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
            detail="Contract not found",
        )

    create_audit_log(
        db=db,
        user_id=get_user_id(current_user),
        action="Deleted contract",
        entity_type="Contract",
        entity_id=contract.id,
        contract_id=contract.id,
        details=f"Contract {contract.contract_number} deleted",
    )

    db.delete(contract)
    db.commit()

    return None


# =========================================================
# CONTRACT WORKFLOW
# =========================================================

@router.patch(
    "/{contract_id}/status",
    response_model=ContractRead,
)
def update_contract_status(
    contract_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
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

    current_status = contract.status

    allowed_transitions = {
        "Draft": {"Under Review"},
        "Under Review": {"Approved"},
        "Approved": {"Active"},
        "Active": {"Expired"},
        "Expired": set(),
    }

    allowed_next_statuses = allowed_transitions.get(
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

    # -----------------------------------------------------
    # Determine required permission
    # -----------------------------------------------------

    required_permission = None

    if (
        current_status == "Draft"
        and new_status == "Under Review"
    ):
        required_permission = Permission.SUBMIT_FOR_REVIEW

    elif (
        current_status == "Under Review"
        and new_status == "Approved"
    ):
        required_permission = Permission.APPROVE_CONTRACT

    elif (
        current_status == "Approved"
        and new_status == "Active"
    ):
        required_permission = Permission.ACTIVATE_CONTRACT

    elif (
        current_status == "Active"
        and new_status == "Expired"
    ):
        required_permission = Permission.EXPIRE_CONTRACT

    if required_permission is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported workflow transition",
        )

    # -----------------------------------------------------
    # RBAC check
    # -----------------------------------------------------

    role = current_user.get("role")

    if not has_permission(role, required_permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"Role '{role}' does not have permission "
                f"'{required_permission.value}'"
            ),
        )

    # -----------------------------------------------------
    # Apply status
    # -----------------------------------------------------

    now = datetime.now(timezone.utc)

    contract.status = new_status
    contract.updated_at = now

    if new_status == "Under Review":
        contract.reviewed_at = now

    elif new_status == "Approved":
     contract.approved_at = now

    audit_log = AuditLog(
        user_id=get_user_id(current_user),
        contract_id=contract.id,
        action="Contract status changed",
        entity_type="Contract",
        entity_id=contract.id,
        details=f"{current_status} -> {new_status}",
    )

    db.add(audit_log)

    db.commit()
    db.refresh(contract)

    return contract

