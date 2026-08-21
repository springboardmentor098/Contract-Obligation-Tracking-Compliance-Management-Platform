from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.user import User
from app.schemas.contract import (
    ContractCreate,
    ContractUpdate,
    ContractStatusUpdate,
    ContractAssignment,
    ContractResponse
)
from app.routers.dependencies import (
    get_current_user,
    require_roles
)
from app.core.roles import UserRole


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)


# CREATE CONTRACT
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
    contract = Contract(
        title=contract_data.title,
        contract_number=contract_data.contract_number,
        category=contract_data.category,
        description=contract_data.description,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        status="Draft",
        created_by=current_user.id
    )

    db.add(contract)

    try:
        db.commit()
        db.refresh(contract)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contract number already exists"
        )

    return contract


# GET ALL CONTRACTS
@router.get(
    "",
    response_model=list[ContractResponse]
)
def get_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contracts = db.query(Contract).all()

    return contracts


# GET CONTRACT BY ID
@router.get(
    "/{contract_id}",
    response_model=ContractResponse
)
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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


# UPDATE CONTRACT
@router.put(
    "/{contract_id}",
    response_model=ContractResponse
)
def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    update_data = contract_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(contract, field, value)

    contract.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(contract)

    return contract


# UPDATE CONTRACT STATUS
@router.patch(
    "/{contract_id}/status",
    response_model=ContractResponse
)
def update_contract_status(
    contract_id: int,
    status_data: ContractStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    current_status = contract.status
    new_status = status_data.status

    valid_statuses = {
        "Draft",
        "Under Review",
        "Approved",
        "Active",
        "Expired",
        "Terminated"
    }

    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid contract status"
        )

    valid_transitions = {
        "Draft": ["Under Review", "Terminated"],
        "Under Review": ["Approved", "Draft", "Terminated"],
        "Approved": ["Active", "Terminated"],
        "Active": ["Expired", "Terminated"],
        "Expired": [],
        "Terminated": []
    }

    if new_status not in valid_transitions.get(
        current_status, []
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status transition: "
                f"{current_status} → {new_status}"
            )
        )

    contract.status = new_status
    contract.updated_at = datetime.now(timezone.utc)

    if new_status == "Under Review":
        contract.reviewed_at = datetime.now(timezone.utc)

    if new_status == "Approved":
        contract.approved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(contract)

    return contract


# ASSIGN CONTRACT
@router.patch(
    "/{contract_id}/assign",
    response_model=ContractResponse
)
def assign_contract(
    contract_id: int,
    assignment_data: ContractAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMINISTRATOR,
            UserRole.LEGAL_MANAGER,
            UserRole.CONTRACT_MANAGER,
            UserRole.DEPARTMENT_HEAD
        )
    )
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if assignment_data.assigned_to is not None:
        assigned_user = db.query(User).filter(
            User.id == assignment_data.assigned_to
        ).first()

        if assigned_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found"
            )

    contract.assigned_to = assignment_data.assigned_to
    contract.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(contract)

    return contract


# SUBMIT CONTRACT FOR REVIEW
@router.post(
    "/{contract_id}/submit-review",
    response_model=ContractResponse
)
def submit_contract_for_review(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMINISTRATOR,
            UserRole.LEGAL_MANAGER,
            UserRole.CONTRACT_MANAGER,
            UserRole.DEPARTMENT_HEAD
        )
    )
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if contract.status != "Draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only contracts in Draft status "
                "can be submitted for review"
            )
        )

    contract.status = "Under Review"
    contract.reviewed_at = datetime.now(timezone.utc)
    contract.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(contract)

    return contract


# APPROVE CONTRACT
@router.post(
    "/{contract_id}/approve",
    response_model=ContractResponse
)
def approve_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMINISTRATOR,
            UserRole.LEGAL_MANAGER,
            UserRole.COMPLIANCE_OFFICER
        )
    )
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if contract.status != "Under Review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only contracts under review "
                "can be approved"
            )
        )

    contract.status = "Approved"
    contract.approved_at = datetime.now(timezone.utc)
    contract.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(contract)

    return contract


# ACTIVATE CONTRACT
@router.post(
    "/{contract_id}/activate",
    response_model=ContractResponse
)
def activate_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMINISTRATOR,
            UserRole.LEGAL_MANAGER,
            UserRole.CONTRACT_MANAGER
        )
    )
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if contract.status != "Approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only approved contracts "
                "can be activated"
            )
        )

    contract.status = "Active"
    contract.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(contract)

    return contract