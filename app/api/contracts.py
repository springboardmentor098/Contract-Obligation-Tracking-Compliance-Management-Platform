from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.user import User
from app.schemas.contract import (
    ContractCreate,
    ContractResponse,
    ContractUpdate,
    ContractStatusUpdate,
    ContractAssignment,
)
from app.schemas.obligation import ObligationResponse
from app.utils.authorization import get_current_user
from app.services.notification_service import (
    generate_contract_approval_notification,
    generate_contract_status_notification,
)


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)


ALLOWED_STATUSES = {
    "Draft",
    "Under Review",
    "Approved",
    "Active",
    "Expired",
    "Terminated",
}


ALLOWED_TRANSITIONS = {
    "Draft": {"Under Review", "Terminated"},
    "Under Review": {"Approved", "Draft", "Terminated"},
    "Approved": {"Active", "Terminated"},
    "Active": {"Expired", "Terminated"},
    "Expired": set(),
    "Terminated": set(),
}


def get_contract_or_404(
    contract_id: int,
    db: Session
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return contract


def get_user_role(current_user: dict) -> str:
    return current_user.get("role", "")


def require_reviewer_or_admin(current_user: dict):
    role = get_user_role(current_user)

    if role not in {"Administrator", "Legal Manager", "Contract Manager"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this operation"
        )


@router.post(
    "",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED
)
def create_contract(
    contract_data: ContractCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing_contract = db.query(Contract).filter(
        Contract.contract_number == contract_data.contract_number
    ).first()

    if existing_contract:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract number already exists"
        )

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    contract = Contract(
        title=contract_data.title,
        contract_number=contract_data.contract_number,
        category=contract_data.category,
        description=contract_data.description,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        status="Draft",
        created_by=current_user["user_id"],
        assigned_to=None,
        reviewed_at=None,
        approved_at=None,
        created_at=now,
        updated_at=now
    )

    db.add(contract)

    try:
        db.commit()
        db.refresh(contract)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract number already exists"
        )

    return contract


@router.get(
    "",
    response_model=list[ContractResponse],
    status_code=status.HTTP_200_OK
)
def get_contracts(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Contract).all()


@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def get_contract(
    contract_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_contract_or_404(contract_id, db)


@router.put(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = get_contract_or_404(contract_id, db)

    if contract.created_by != current_user["user_id"] and \
       contract.assigned_to != current_user["user_id"] and \
       get_user_role(current_user) not in {"Administrator", "Legal Manager", "Contract Manager"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this contract"
        )

    update_data = contract_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(contract, field, value)

    contract.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    db.commit()
    db.refresh(contract)

    return contract


@router.patch(
    "/{contract_id}/status",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def update_contract_status(
    contract_id: int,
    status_data: ContractStatusUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = get_contract_or_404(contract_id, db)

    new_status = status_data.status

    if new_status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid contract status"
        )

    if new_status not in ALLOWED_TRANSITIONS.get(contract.status, set()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition: {contract.status} -> {new_status}"
        )

    if new_status in {"Under Review", "Approved"}:
        require_reviewer_or_admin(current_user)

    contract.status = new_status

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    if new_status == "Under Review":
        contract.reviewed_at = now

    if new_status == "Approved":
        contract.approved_at = now

    contract.updated_at = now

    db.commit()
    db.refresh(contract)

    return contract


@router.post(
    "/{contract_id}/submit-review",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def submit_contract_for_review(
    contract_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = get_contract_or_404(contract_id, db)

    if contract.status != "Draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Draft contracts can be submitted for review"
        )

    contract.status = "Under Review"
    contract.reviewed_at = datetime.now(timezone.utc).replace(tzinfo=None)
    contract.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    db.commit()
    db.refresh(contract)

    # Notify active Legal Managers.
    legal_managers = db.query(User).filter(
        User.role == "Legal Manager",
        User.is_active == True,
    ).all()

    for manager in legal_managers:
        generate_contract_approval_notification(
            db=db,
            contract=contract,
            user_id=manager.id,
        )

    # Notify the contract creator.
    generate_contract_status_notification(
        db=db,
        contract=contract,
        user_id=contract.created_by,
    )

    return contract


@router.post(
    "/{contract_id}/approve",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def approve_contract(
    contract_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_reviewer_or_admin(current_user)

    contract = get_contract_or_404(contract_id, db)

    if contract.status != "Under Review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only contracts under review can be approved"
        )

    contract.status = "Approved"
    contract.approved_at = datetime.now(timezone.utc).replace(tzinfo=None)
    contract.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    db.commit()
    db.refresh(contract)

    # Notify the contract creator that the contract was approved.
    generate_contract_status_notification(
        db=db,
        contract=contract,
        user_id=contract.created_by,
    )

    return contract


@router.post(
    "/{contract_id}/activate",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def activate_contract(
    contract_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = get_contract_or_404(contract_id, db)

    if contract.status != "Approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only approved contracts can be activated"
        )

    if contract.created_by != current_user["user_id"] and \
       contract.assigned_to != current_user["user_id"] and \
       get_user_role(current_user) not in {"Administrator", "Legal Manager", "Contract Manager"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to activate this contract"
        )

    contract.status = "Active"
    contract.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    db.commit()
    db.refresh(contract)

    # Notify the contract creator that the contract is now active.
    generate_contract_status_notification(
        db=db,
        contract=contract,
        user_id=contract.created_by,
    )

    return contract


@router.patch(
    "/{contract_id}/assignment",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def assign_contract(
    contract_id: int,
    assignment_data: ContractAssignment,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = get_contract_or_404(contract_id, db)

    if get_user_role(current_user) not in {"Administrator", "Legal Manager", "Contract Manager"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Administrator, Legal Manager, or Contract Manager can assign contracts"
        )

    if assignment_data.assigned_to is not None:
        user = db.query(User).filter(
            User.id == assignment_data.assigned_to
        ).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found"
            )

    contract.assigned_to = assignment_data.assigned_to
    contract.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    db.commit()
    db.refresh(contract)

    return contract
