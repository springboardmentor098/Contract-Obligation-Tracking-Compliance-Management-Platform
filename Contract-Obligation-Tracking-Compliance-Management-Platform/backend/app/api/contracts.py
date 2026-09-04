from datetime import datetime

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
    ContractAssignmentResponse,
    ContractResponse,
)
from app.core.security import get_current_user
from app.models.obligation import Obligation

from app.schemas.compliance import ComplianceResponse

from app.services.compliance_service import (
    calculate_contract_compliance,
)


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)


# ============================================================
# Create Contract
# ============================================================

@router.post(
    "/",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED
)
def create_contract(
    contract_data: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check duplicate contract number
    existing_contract = (
        db.query(Contract)
        .filter(
            Contract.contract_number
            == contract_data.contract_number
        )
        .first()
    )

    if existing_contract:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract number already exists"
        )

    # Validate dates
    if contract_data.end_date < contract_data.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date cannot be before start date"
        )

    # Create contract
    contract = Contract(
        title=contract_data.title,
        contract_number=contract_data.contract_number,
        category=contract_data.category,
        description=contract_data.description,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,

        # Backend-controlled values
        status="Draft",
        created_by=current_user.id
    )

    try:
        db.add(contract)
        db.commit()
        db.refresh(contract)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create contract"
        )

    return contract


# ============================================================
# Get All Contracts
# ============================================================

@router.get(
    "/",
    response_model=list[ContractResponse]
)
def get_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contracts = (
        db.query(Contract)
        .order_by(Contract.id)
        .all()
    )

    return contracts


@router.get(
    "/{contract_id}/compliance",
    response_model=ComplianceResponse,
)
def get_contract_compliance(
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
            status_code=404,
            detail="Contract not found",
        )

    obligations = (
        db.query(Obligation)
        .filter(
            Obligation.contract_id == contract_id
        )
        .all()
    )

    return calculate_contract_compliance(
        contract,
        obligations,
    )


# ============================================================
# Get Contract By ID
# ============================================================

@router.get(
    "/{contract_id}",
    response_model=ContractResponse
)
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id
        )
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return contract


# ============================================================
# UPDATE CONTRACT
# PUT /contracts/{contract_id}
# ============================================================

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
    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id
        )
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    update_data = contract_data.model_dump(
        exclude_unset=True
    )

    # Check date validity
    new_start_date = update_data.get(
        "start_date",
        contract.start_date
    )

    new_end_date = update_data.get(
        "end_date",
        contract.end_date
    )

    if new_end_date < new_start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date cannot be before start date"
        )

    # Update allowed fields only
    for field, value in update_data.items():
        setattr(contract, field, value)

    contract.updated_at = datetime.utcnow()

    try:
        db.commit()
        db.refresh(contract)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to update contract"
        )

    return contract


APPROVER_ROLES = {
    "Administrator",
    "Legal Manager",
    "Compliance Officer",
    "Contract Manager",
    "Department Head",
}


# ============================================================
# CHANGE CONTRACT STATUS
# PATCH /contracts/{contract_id}/status
# ============================================================

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
    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id
        )
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    current_status = contract.status
    new_status = status_data.status

    if new_status == "Approved" and current_user.role not in APPROVER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only authorized users have permission to approve contracts"
        )

    # Allowed lifecycle transitions
    valid_transitions = {
        "Draft": ["Under Review"],
        "Under Review": ["Approved"],
        "Approved": ["Active"],
        "Active": ["Expired", "Terminated"],
        "Expired": [],
        "Terminated": []
    }

    if new_status not in valid_transitions.get(
        current_status,
        []
    ):
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

    if new_status == "Approved":
        contract.approved_at = datetime.utcnow()

    contract.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# SUBMIT CONTRACT FOR REVIEW
# POST /contracts/{contract_id}/submit-review
# ============================================================

@router.post(
    "/{contract_id}/submit-review",
    response_model=ContractResponse
)
def submit_contract_for_review(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id
        )
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if contract.status != "Draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only Draft contracts can "
                "be submitted for review"
            )
        )

    contract.status = "Under Review"
    contract.reviewed_at = datetime.utcnow()
    contract.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# APPROVE CONTRACT
# POST /contracts/{contract_id}/approve
# ============================================================

@router.post(
    "/{contract_id}/approve",
    response_model=ContractResponse
)
def approve_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in APPROVER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only authorized users have permission to approve contracts"
        )

    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id
        )
        .first()
    )

    if not contract:
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
    contract.approved_at = datetime.utcnow()
    contract.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# ACTIVATE CONTRACT
# POST /contracts/{contract_id}/activate
# ============================================================

@router.post(
    "/{contract_id}/activate",
    response_model=ContractResponse
)
def activate_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id
        )
        .first()
    )

    if not contract:
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
    contract.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# ASSIGN CONTRACT
# PATCH /contracts/{contract_id}/assignment
# ============================================================

@router.patch(
    "/{contract_id}/assignment",
    response_model=ContractResponse
)
def assign_contract(
    contract_id: int,
    assignment_data: ContractAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id
        )
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Check assigned user exists
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
            detail="Assigned user not found"
        )

    contract.assigned_to = assignment_data.assigned_to
    contract.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract
