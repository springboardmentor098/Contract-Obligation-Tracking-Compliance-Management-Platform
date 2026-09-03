from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.renewal import Renewal
from app.models.contract import Contract
from app.models.user import User
from app.schemas.renewal import (
    RenewalCreate,
    RenewalUpdate,
    RenewalStatusUpdate,
    RenewalResponse,
    RenewalComplete,
)
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/renewals",
    tags=["Renewals"]
)


ALLOWED_STATUSES = {
    "Upcoming",
    "In Progress",
    "Renewed",
    "Expired",
    "Cancelled"
}


def get_renewal_or_404(
    renewal_id: int,
    db: Session
):
    renewal = (
        db.query(Renewal)
        .filter(Renewal.id == renewal_id)
        .first()
    )

    if renewal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found"
        )

    return renewal


def check_contract_access(
    renewal: Renewal,
    current_user: User,
    db: Session
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == renewal.contract_id)
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
        and renewal.assigned_to != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this renewal"
        )

    return contract


@router.post(
    "/",
    response_model=RenewalResponse,
    status_code=status.HTTP_201_CREATED
)
def create_renewal(
    renewal_data: RenewalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == renewal_data.contract_id)
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
            detail="You do not have permission to create a renewal for this contract"
        )

    assigned_user = (
        db.query(User)
        .filter(User.id == renewal_data.assigned_to)
        .first()
    )

    if assigned_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )

    if renewal_data.new_expiry_date is not None:
        if renewal_data.new_expiry_date < renewal_data.renewal_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="New expiry date cannot be earlier than renewal date"
            )

        if renewal_data.new_expiry_date <= renewal_data.previous_expiry_date:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="New expiry date should be later than previous expiry date"
            )

    if renewal_data.previous_expiry_date != contract.end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Previous expiry date must match the contract expiry date"
        )

    renewal = Renewal(
        contract_id=renewal_data.contract_id,
        assigned_to=renewal_data.assigned_to,
        renewal_date=renewal_data.renewal_date,
        previous_expiry_date=renewal_data.previous_expiry_date,
        new_expiry_date=renewal_data.new_expiry_date,
        status="Upcoming",
        notes=renewal_data.notes,
        notice_days=30
    )

    db.add(renewal)
    db.commit()
    db.refresh(renewal)

    return renewal


@router.get(
    "/",
    response_model=list[RenewalResponse]
)
def get_renewals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    renewals = (
        db.query(Renewal)
        .join(
            Contract,
            Renewal.contract_id == Contract.id
        )
        .filter(
            (Contract.owner_id == current_user.id)
            | (Contract.assigned_to == current_user.id)
            | (Renewal.assigned_to == current_user.id)
        )
        .all()
    )

    return renewals



@router.get(
    "/upcoming",
    response_model=list[RenewalResponse]
)
def get_upcoming_renewals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()

    # Contracts expiring within the next 90 days
    expiry_limit = date.fromordinal(
        today.toordinal() + 90
    )

    renewals = (
        db.query(Renewal)
        .join(
            Contract,
            Renewal.contract_id == Contract.id
        )
        .filter(
            (
                (Contract.owner_id == current_user.id)
                | (Contract.assigned_to == current_user.id)
                | (Renewal.assigned_to == current_user.id)
            ),
            Contract.end_date >= today,
            Contract.end_date <= expiry_limit,
            Renewal.status == "Upcoming"
        )
        .all()
    )

    return renewals

@router.get(
    "/expired-contracts",
    response_model=list[RenewalResponse]
)
def get_expired_contract_renewals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()

    renewals = (
        db.query(Renewal)
        .join(
            Contract,
            Renewal.contract_id == Contract.id
        )
        .filter(
            (
                (Contract.owner_id == current_user.id)
                | (Contract.assigned_to == current_user.id)
                | (Renewal.assigned_to == current_user.id)
            ),
            Contract.end_date < today,
            Renewal.status == "Upcoming"
        )
        .all()
    )

    return renewals


@router.get(
    "/{renewal_id}",
    response_model=RenewalResponse
)
def get_renewal(
    renewal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    renewal = get_renewal_or_404(
        renewal_id,
        db
    )

    check_contract_access(
        renewal,
        current_user,
        db
    )

    return renewal

@router.put(
    "/{renewal_id}",
    response_model=RenewalResponse
)
def update_renewal(
    renewal_id: int,
    renewal_data: RenewalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    renewal = get_renewal_or_404(
        renewal_id,
        db
    )

    contract = check_contract_access(
        renewal,
        current_user,
        db
    )

    update_data = renewal_data.model_dump(
        exclude_unset=True
    )

    # Validate assigned user
    if "assigned_to" in update_data:
        assigned_user = (
            db.query(User)
            .filter(
                User.id == update_data["assigned_to"],
                User.is_active == True
            )
            .first()
        )

        if assigned_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found or inactive"
            )

    # Validate new expiry date
    if "new_expiry_date" in update_data:
        new_expiry_date = update_data["new_expiry_date"]

        if new_expiry_date is not None:
            renewal_date = update_data.get(
                "renewal_date",
                renewal.renewal_date
            )

            if new_expiry_date < renewal_date:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="New expiry date cannot be earlier than renewal date"
                )

            if new_expiry_date <= renewal.previous_expiry_date:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="New expiry date should be later than previous expiry date"
                )

    # Validate renewal date if it is being changed
    if "renewal_date" in update_data:
        new_renewal_date = update_data["renewal_date"]

        if (
            renewal.new_expiry_date is not None
            and new_renewal_date > renewal.new_expiry_date
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Renewal date cannot be later than new expiry date"
            )

    for field, value in update_data.items():
        setattr(renewal, field, value)

    db.commit()
    db.refresh(renewal)

    return renewal

@router.patch(
    "/{renewal_id}/status",
    response_model=RenewalResponse
)
def update_renewal_status(
    renewal_id: int,
    status_data: RenewalStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    renewal = get_renewal_or_404(
        renewal_id,
        db
    )

    check_contract_access(
        renewal,
        current_user,
        db
    )

    new_status = status_data.status

    if new_status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid renewal status"
        )

    current_status = renewal.status

    valid_transitions = {
        "Upcoming": {
            "In Progress",
            "Expired",
            "Cancelled"
        },
        "In Progress": {
            "Renewed",
            "Cancelled"
        },
        "Renewed": set(),
        "Expired": set(),
        "Cancelled": set()
    }

    if new_status == current_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Renewal is already in this status"
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

    renewal.status = new_status

    db.commit()
    db.refresh(renewal)

    return renewal

@router.post(
    "/{renewal_id}/renew",
    response_model=RenewalResponse
)
def complete_renewal(
    renewal_id: int,
    renewal_data: RenewalComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    renewal = get_renewal_or_404(
        renewal_id,
        db
    )

    contract = check_contract_access(
        renewal,
        current_user,
        db
    )

    if renewal.status != "In Progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only renewals in progress can be completed"
        )

    if renewal_data.new_expiry_date <= renewal.renewal_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New expiry date must be later than renewal date"
        )

    if renewal_data.new_expiry_date <= renewal.previous_expiry_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New expiry date must be later than previous expiry date"
        )

    renewal.new_expiry_date = renewal_data.new_expiry_date
    renewal.status = "Renewed"

    # Update the associated contract's expiry date
    contract.end_date = renewal_data.new_expiry_date

    db.commit()
    db.refresh(renewal)

    return renewal

