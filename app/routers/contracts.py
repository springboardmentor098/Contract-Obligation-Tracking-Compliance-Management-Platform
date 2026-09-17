from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.obligation import Obligation
from app.database.database import get_db
from app.models.contract import Contract
from app.models.user import User
from datetime import date
from app.models.renewal import Renewal
from app.schemas.contract import (
    ContractAssignment,
    ContractCreate,
    ContractResponse,
    ContractStatusUpdate,
    ContractUpdate,
)
from app.core.dependencies import get_current_user
from app.services.compliance_service import calculate_contract_compliance
from app.schemas.compliance import ComplianceResponse
from app.services.compliance_service import (
    calculate_contract_compliance,
    save_compliance_history
)


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)


# ---------------------------------------------------------
# CREATE CONTRACT
# ---------------------------------------------------------

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

        # Automatically create a renewal record for an already expired contract
        if contract.end_date < date.today():
            contract.status = "Expired"
        db.commit()
        db.refresh(contract)
        renewal = Renewal(
                contract_id=contract.id,
                renewal_date=date.today(),
                previous_expiry_date=contract.end_date,
                new_expiry_date=contract.end_date,
                renewal_status="Upcoming",
                assigned_to=current_user.id,
                notes="Automatically created for expired contract"
            )

        db.add(renewal)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contract number already exists"
        )

    return contract


# ---------------------------------------------------------
# GET ALL CONTRACTS
# ---------------------------------------------------------

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

# ---------------------------------------------------------
# GET OBLIGATIONS FOR CONTRACT
# ---------------------------------------------------------

@router.get(
    "/{contract_id}/obligations",
    status_code=status.HTTP_200_OK
)
def get_contract_obligations(
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
            detail="Contract not found"
        )

    obligations = (
        db.query(Obligation)
        .filter(Obligation.contract_id == contract_id)
        .all()
    )

    return obligations
# ---------------------------------------------------------
# GET CONTRACT BY ID
# ---------------------------------------------------------

@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def get_contract(
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
            detail="Contract not found"
        )

    return contract


# ---------------------------------------------------------
# UPDATE CONTRACT
# ---------------------------------------------------------

@router.put(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
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
            detail="Contract not found"
        )

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


# ---------------------------------------------------------
# ASSIGN CONTRACT
# ---------------------------------------------------------

@router.patch(
    "/{contract_id}/assign",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def assign_contract(
    contract_id: int,
    assignment_data: ContractAssignment,
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
            detail="Contract not found"
        )

    assigned_user = (
        db.query(User)
        .filter(User.id == assignment_data.assigned_to)
        .first()
    )

    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )

    contract.assigned_to = assigned_user.id

    db.commit()
    db.refresh(contract)

    return contract


# ---------------------------------------------------------
# UPDATE STATUS
# ---------------------------------------------------------

@router.patch(
    "/{contract_id}/status",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def update_contract_status(
    contract_id: int,
    status_data: ContractStatusUpdate,
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
            detail="Contract not found"
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

    contract.status = status_data.status

    db.commit()
    db.refresh(contract)

    return contract


# ---------------------------------------------------------
# SUBMIT FOR REVIEW
# ---------------------------------------------------------

@router.post(
    "/{contract_id}/submit-review",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def submit_for_review(
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
            detail="Contract not found"
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


# ---------------------------------------------------------
# APPROVE CONTRACT
# ---------------------------------------------------------

@router.post(
    "/{contract_id}/approve",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def approve_contract(
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
            detail="Contract not found"
        )

    if current_user.role not in ["Administrator", "Legal Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to approve contracts"
        )

    if contract.status != "Under Review":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Under Review contracts can be approved"
        )

    contract.status = "Approved"
    contract.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract


# ---------------------------------------------------------
# ACTIVATE CONTRACT
# ---------------------------------------------------------

@router.post(
    "/{contract_id}/activate",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def activate_contract(
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
            detail="Contract not found"
        )

    if contract.status != "Approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Approved contracts can be activated"
        )

    contract.status = "Active"

    db.commit()
    db.refresh(contract)

    return contract
@router.get(
    "/{contract_id}/compliance",
    response_model=ComplianceResponse
)
def get_contract_compliance(
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
            detail="Contract not found"
        )

    obligations = (
        db.query(Obligation)
        .filter(Obligation.contract_id == contract_id)
        .all()
    )

    compliance_data = calculate_contract_compliance(obligations)

    save_compliance_history(
        db=db,
        contract_id=contract.id,
        compliance_data=compliance_data
    )

    return {
        "contract_id": contract.id,
        **compliance_data
    }