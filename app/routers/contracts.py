from datetime import datetime

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
from app.dependencies import get_current_user
from app.core.roles import UserRole


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)


# =========================
# CREATE CONTRACT
# =========================

@router.post(
    "",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED
)
def create_contract(
    contract_data: ContractCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing_contract = db.query(Contract).filter(
        Contract.contract_number == contract_data.contract_number
    ).first()

    if existing_contract:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract number already exists"
        )

    contract = Contract(
        contract_number=contract_data.contract_number,
        title=contract_data.title,
        category=contract_data.category,
        description=contract_data.description,
        party_name=contract_data.party_name,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        status="Draft",
        owner_id=current_user["user_id"]
    )

    try:
        db.add(contract)
        db.commit()
        db.refresh(contract)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract number already exists"
        )

    return contract


# =========================
# GET ALL CONTRACTS
# =========================

@router.get(
    "",
    response_model=list[ContractResponse],
    status_code=status.HTTP_200_OK
)
def get_contracts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    contracts = db.query(Contract).all()

    return contracts


# =========================
# GET CONTRACT BY ID
# =========================

@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
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


# =========================
# UPDATE CONTRACT
# =========================

@router.put(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if contract.owner_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this contract"
        )

    update_data = contract_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(contract, field, value)

    db.commit()
    db.refresh(contract)

    return contract


# =========================
# UPDATE CONTRACT STATUS
# =========================

@router.patch(
    "/{contract_id}/status",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def update_contract_status(
    contract_id: int,
    status_data: ContractStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if contract.owner_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to change this contract status"
        )

    current_status = contract.status
    new_status = status_data.status

    valid_transitions = {
        "Draft": ["Under Review"],
        "Under Review": ["Approved"],
        "Approved": ["Active"],
        "Active": ["Expired", "Terminated"],
        "Expired": [],
        "Terminated": []
    }

    if new_status not in valid_transitions.get(current_status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from {current_status} to {new_status}"
        )

    contract.status = new_status

    if new_status == "Under Review":
        contract.reviewed_at = datetime.utcnow()

    if new_status == "Approved":
        contract.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


# =========================
# SUBMIT FOR REVIEW
# =========================

@router.post(
    "/{contract_id}/submit-review",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def submit_for_review(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if contract.owner_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to submit this contract"
        )

    if contract.status != "Draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Draft contracts can be submitted for review"
        )

    contract.status = "Under Review"
    contract.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


# =========================
# APPROVE CONTRACT
# =========================

@router.post(
    "/{contract_id}/approve",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def approve_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if current_user["role"] != UserRole.ADMINISTRATOR.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can approve contracts"
        )

    if contract.status != "Under Review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only contracts under review can be approved"
        )

    contract.status = "Approved"
    contract.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


# =========================
# ACTIVATE CONTRACT
# =========================

@router.post(
    "/{contract_id}/activate",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def activate_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if contract.owner_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to activate this contract"
        )

    if contract.status != "Approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only approved contracts can be activated"
        )

    contract.status = "Active"

    db.commit()
    db.refresh(contract)

    return contract


# =========================
# ASSIGN CONTRACT
# =========================

@router.patch(
    "/{contract_id}/assign",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def assign_contract(
    contract_id: int,
    assignment_data: ContractAssignment,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if contract.owner_id != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to assign this contract"
        )

    assigned_user = db.query(User).filter(
        User.id == assignment_data.assigned_to
    ).first()

    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )

    contract.assigned_to = assigned_user.id

    db.commit()
    db.refresh(contract)

    return contract