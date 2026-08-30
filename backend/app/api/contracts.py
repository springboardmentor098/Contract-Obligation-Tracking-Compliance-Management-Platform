from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.contract import Contract
from backend.app.models.user import User
from backend.app.schemas.contract import (
    ContractCreate,
    ContractUpdate,
    ContractStatusUpdate,
    ContractAssignment,
    ContractOut
)
from backend.app.services.notification_service import (
    create_approval_notification,
    create_contract_approved_notification
)
from backend.app.core.auth import get_current_user


router = APIRouter()

# SUBMIT CONTRACT FOR REVIEW
@router.post(
    "/{contract_id}/submit-review",
    response_model=ContractOut
)
def submit_contract_for_review(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found"
        )

    # Contract must be in Draft status
    if contract.status != "Draft":
        raise HTTPException(
            status_code=400,
            detail="Only Draft contracts can be submitted for review"
        )

    # Change status
    contract.status = "Under Review"

    # Record review time
    contract.reviewed_at = datetime.utcnow()

    # Create approval notification
    create_approval_notification(
        db=db,
        user_id=contract.owner_id,
        contract_id=contract.id,
        contract_number=contract.contract_number
    )

    db.refresh(contract)

    return contract
# APPROVE CONTRACT
@router.post(
    "/{contract_id}/approve",
    response_model=ContractOut
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
            status_code=404,
            detail="Contract not found"
        )

    if contract.status != "Under Review":
        raise HTTPException(
            status_code=400,
            detail="Only contracts under review can be approved"
        )

    allowed_roles = [
        "Administrator",
        "Legal Manager"
    ]

    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to approve contracts"
        )

    # Approve contract
    contract.status = "Approved"
    contract.approved_at = datetime.utcnow()

    # Create approval notification
    create_contract_approved_notification(
        db=db,
        user_id=contract.owner_id,
        contract_id=contract.id,
        contract_number=contract.contract_number
    )

    db.refresh(contract)

    return contract
# CREATE CONTRACT
@router.post(
    "/",
    response_model=ContractOut,
    status_code=status.HTTP_201_CREATED
)
def create_contract(
    contract: ContractCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    # Find logged-in user
    user = db.query(User).filter(
        User.email == current_user["email"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Check duplicate contract number
    existing = db.query(Contract).filter(
        Contract.contract_number == contract.contract_number
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Contract number already exists"
        )

    # Create contract
    db_contract = Contract(
        owner_id=user.id,
        contract_number=contract.contract_number,
        title=contract.title,
        category=contract.category,
        description=contract.description,
        start_date=contract.start_date,
        end_date=contract.end_date,
        status="Draft"
    )

    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)

    return db_contract


# GET ALL CONTRACTS
@router.get(
    "/",
    response_model=list[ContractOut]
)
def get_contracts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    contracts = db.query(Contract).all()

    return contracts


# UPDATE CONTRACT
@router.put(
    "/{contract_id}",
    response_model=ContractOut
)
def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    # Find contract
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found"
        )

    # Update only fields provided by the user
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

    db.commit()
    db.refresh(contract)

    return contract
# ASSIGN CONTRACT
@router.patch(
    "/{contract_id}/assign",
    response_model=ContractOut
)
def assign_contract(
    contract_id: int,
    assignment: ContractAssignment,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    # Find contract
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found"
        )

    # Find assigned user
    user = db.query(User).filter(
        User.id == assignment.assigned_to
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Assigned user not found"
        )

    # Assign contract
    contract.assigned_to = user.id

    db.commit()
    db.refresh(contract)

    return contract
# UPDATE CONTRACT STATUS
@router.patch(
    "/{contract_id}/status",
    response_model=ContractOut
)
def update_contract_status(
    contract_id: int,
    status_data: ContractStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    # Find contract
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found"
        )

    # Supported statuses
    allowed_statuses = [
        "Draft",
        "Under Review",
        "Approved",
        "Active",
        "Expired",
        "Terminated"
    ]

    if status_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid contract status"
        )

    # Valid workflow transitions
    valid_transitions = {
        "Draft": ["Under Review"],
        "Under Review": ["Approved"],
        "Approved": ["Active"],
        "Active": ["Expired", "Terminated"],
        "Expired": [],
        "Terminated": []
    }

    current_status = contract.status
    new_status = status_data.status

    # Check transition
    if new_status not in valid_transitions[current_status]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition: {current_status} → {new_status}"
        )

    # Update status
    contract.status = new_status

    # Set timestamps
    if new_status == "Under Review":
        contract.reviewed_at = datetime.utcnow()

    if new_status == "Approved":
        contract.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract