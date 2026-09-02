from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.user import User
from app.models.obligation import Obligation
from app.models.renewal import Renewal

from app.schemas.contract import (
    ContractCreate,
    ContractResponse,
    ContractUpdate,
    ContractStatusUpdate,
    ContractAssignment,
)

from app.schemas.obligation import ObligationResponse
from app.schemas.renewal import RenewalResponse
from app.schemas.compliance import ComplianceResponse

from app.services.compliance_service import calculate_contract_compliance

from app.services.notification_service import (
    notify_contract_submitted_for_review,
    notify_contract_approved,
    notify_contract_status_changed,
)

from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)


def get_owned_contract(
    contract_id: int,
    current_user: User,
    db: Session
):
    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id,
            Contract.owner_id == current_user.id
        )
        .first()
    )

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return contract


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
    contract = Contract(
        owner_id=current_user.id,
        contract_code=contract_data.contract_code,
        title=contract_data.title,
        description=contract_data.description,
        counterparty=contract_data.counterparty,
        category=contract_data.category,
        status="Draft",
        risk_level=contract_data.risk_level,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date
    )

    db.add(contract)

    try:
        db.commit()
        db.refresh(contract)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contract code already exists"
        )

    return contract


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
        .filter(
            Contract.owner_id == current_user.id
        )
        .all()
    )

    return contracts


@router.get(
    "/{contract_id}/obligations",
    response_model=list[ObligationResponse]
)
def get_contract_obligations(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id,
            Contract.owner_id == current_user.id
        )
        .first()
    )

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    obligations = (
        db.query(Obligation)
        .filter(
            Obligation.contract_id == contract_id
        )
        .all()
    )

    return obligations


@router.get(
    "/{contract_id}/renewals",
    response_model=list[RenewalResponse]
)
def get_contract_renewals(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id,
            Contract.owner_id == current_user.id
        )
        .first()
    )

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    renewals = (
        db.query(Renewal)
        .filter(
            Renewal.contract_id == contract_id
        )
        .all()
    )

    return renewals


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
        .filter(
            Contract.id == contract_id
        )
        .first()
    )

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if (
        contract.owner_id != current_user.id
        and contract.assigned_to != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission to view "
                "this contract's compliance"
            )
        )

    compliance = calculate_contract_compliance(
        contract_id,
        db
    )

    return {
        "contract_id": contract_id,
        **compliance
    }


@router.get(
    "/{contract_id}",
    response_model=ContractResponse
)
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_owned_contract(
        contract_id,
        current_user,
        db
    )


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
    contract = get_owned_contract(
        contract_id,
        current_user,
        db
    )

    update_data = contract_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(contract, field, value)

    try:
        db.commit()
        db.refresh(contract)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contract update violates a database constraint"
        )

    return contract


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
    contract = get_owned_contract(
        contract_id,
        current_user,
        db
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

    valid_transitions = {
        "Draft": {"Under Review"},
        "Under Review": {"Approved"},
        "Approved": {"Active"},
        "Active": {"Expired", "Terminated"},
        "Expired": set(),
        "Terminated": set()
    }

    current_status = contract.status
    new_status = status_data.status

    if new_status == current_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract is already in this status"
        )

    if new_status not in valid_transitions.get(
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

    now = datetime.utcnow()

    if new_status == "Under Review":
        contract.reviewed_at = now

    if new_status == "Approved":
        contract.approved_at = now

    db.commit()
    db.refresh(contract)

    if new_status not in {"Under Review", "Approved"}:
        notify_contract_status_changed(
            db=db,
            contract=contract,
            old_status=current_status,
            new_status=new_status
        )

    return contract


@router.post(
    "/{contract_id}/submit-review",
    response_model=ContractResponse
)
def submit_for_review(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = get_owned_contract(
        contract_id,
        current_user,
        db
    )

    if contract.status != "Draft":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only Draft contracts can be submitted "
                "for review"
            )
        )

    contract.status = "Under Review"
    contract.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    notify_contract_submitted_for_review(
        db=db,
        contract=contract
    )

    return contract

@router.post(
    "/{contract_id}/approve",
    response_model=ContractResponse
)
def approve_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    allowed_roles = {
        "ADMINISTRATOR",
        "LEGAL_MANAGER"
    }

    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to approve contracts"
        )

    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id
        )
        .first()
    )

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
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

    notify_contract_approved(
        db=db,
        contract=contract
    )

    return contract

@router.post(
    "/{contract_id}/activate",
    response_model=ContractResponse
)
def activate_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = get_owned_contract(
        contract_id,
        current_user,
        db
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


@router.patch(
    "/{contract_id}/assign",
    response_model=ContractResponse
)
def assign_contract(
    contract_id: int,
    assignment_data: ContractAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = get_owned_contract(
        contract_id,
        current_user,
        db
    )

    assigned_user = (
        db.query(User)
        .filter(
            User.id == assignment_data.assigned_to,
            User.is_active == True
        )
        .first()
    )

    if assigned_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found or inactive"
        )

    contract.assigned_to = assigned_user.id

    db.commit()
    db.refresh(contract)

    return contract