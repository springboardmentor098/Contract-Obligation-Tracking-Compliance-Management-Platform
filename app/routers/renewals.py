from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.contract import Contract
from app.models.renewal import Renewal
from app.models.user import User
from app.schemas.renewal import (
    RenewalCreate,
    RenewalResponse,
    RenewalStatusUpdate,
    RenewalUpdate,
)


router = APIRouter(
    prefix="/renewals",
    tags=["Renewals"],
)
contract_router = APIRouter(
    prefix="/contracts",
    tags=["Renewals"],
)
@contract_router.get(
    "/{contract_id}/renewals",
    response_model=list[RenewalResponse],
)
def get_contract_renewals(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    renewals = db.query(Renewal).filter(
        Renewal.contract_id == contract_id
    ).all()

    return renewals


@router.post(
    "",
    response_model=RenewalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_renewal(
    renewal_data: RenewalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contract = db.query(Contract).filter(
        Contract.id == renewal_data.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    if renewal_data.assigned_to is not None:
        assigned_user = db.query(User).filter(
            User.id == renewal_data.assigned_to
        ).first()

        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found",
            )

    if renewal_data.new_expiry_date <= renewal_data.renewal_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New expiry date must be later than renewal date",
        )

    renewal = Renewal(
        contract_id=renewal_data.contract_id,
        renewal_date=renewal_data.renewal_date,
        previous_expiry_date=renewal_data.previous_expiry_date,
        new_expiry_date=renewal_data.new_expiry_date,
        renewal_status="Upcoming",
        assigned_to=renewal_data.assigned_to,
        notes=renewal_data.notes,
    )

    db.add(renewal)
    db.commit()
    db.refresh(renewal)

    return renewal


@router.get(
    "",
    response_model=list[RenewalResponse],
)
def get_renewals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Renewal).all()


@router.get(
    "/{renewal_id}",
    response_model=RenewalResponse,
)
def get_renewal(
    renewal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found",
        )

    return renewal


@router.put(
    "/{renewal_id}",
    response_model=RenewalResponse,
)
def update_renewal(
    renewal_id: int,
    renewal_data: RenewalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found",
        )

    if renewal_data.assigned_to is not None:
        assigned_user = db.query(User).filter(
            User.id == renewal_data.assigned_to
        ).first()

        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found",
            )

    if (
        renewal_data.new_expiry_date is not None
        and renewal_data.new_expiry_date <= renewal.renewal_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New expiry date must be later than renewal date",
        )

    update_data = renewal_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(renewal, field, value)

    db.commit()
    db.refresh(renewal)

    return renewal


@router.patch(
    "/{renewal_id}/status",
    response_model=RenewalResponse,
)
def update_renewal_status(
    renewal_id: int,
    status_data: RenewalStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found",
        )

    allowed_transitions = {
        "Upcoming": ["In Progress", "Expired", "Cancelled"],
        "In Progress": ["Renewed", "Cancelled"],
        "Renewed": [],
        "Expired": [],
        "Cancelled": [],
    }

    new_status = status_data.renewal_status

    if new_status not in allowed_transitions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid renewal status",
        )

    if new_status not in allowed_transitions[renewal.renewal_status]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status transition from "
                f"{renewal.renewal_status} to {new_status}"
            ),
        )

    renewal.renewal_status = new_status

    db.commit()
    db.refresh(renewal)

    return renewal


@router.post(
    "/{renewal_id}/renew",
    response_model=RenewalResponse,
)
def complete_renewal(
    renewal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found",
        )

    if renewal.renewal_status != "In Progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only In Progress renewals can be completed",
        )

    contract = db.query(Contract).filter(
        Contract.id == renewal.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    renewal.renewal_status = "Renewed"
    contract.end_date = renewal.new_expiry_date

    db.commit()
    db.refresh(renewal)

    return renewal