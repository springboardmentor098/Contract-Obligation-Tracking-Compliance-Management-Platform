from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.renewal import Renewal
from backend.app.models.contract import Contract
from backend.app.models.user import User
from backend.app.schemas.renewal import (
    RenewalCreate,
    RenewalUpdate,
    RenewalStatusUpdate,
    RenewalOut
)
from backend.app.core.auth import get_current_user


router = APIRouter(
    prefix="/renewals",
    tags=["Renewals"]
)


# ============================================================
# CREATE RENEWAL
# POST /renewals
# ============================================================

@router.post(
    "",
    response_model=RenewalOut,
    status_code=status.HTTP_201_CREATED
)
def create_renewal(
    renewal: RenewalCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Check contract exists
    contract = db.query(Contract).filter(
        Contract.id == renewal.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Check assigned user exists
    if renewal.assigned_to is not None:
        assigned_user = db.query(User).filter(
            User.id == renewal.assigned_to
        ).first()

        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found"
            )

    # Create renewal
    new_renewal = Renewal(
        contract_id=renewal.contract_id,
        renewal_date=renewal.renewal_date,
        previous_expiry_date=renewal.previous_expiry_date,
        new_expiry_date=renewal.new_expiry_date,
        status="Upcoming",
        assigned_to=renewal.assigned_to,
        notes=renewal.notes
    )

    db.add(new_renewal)
    db.commit()
    db.refresh(new_renewal)

    return new_renewal


# ============================================================
# GET ALL RENEWALS
# GET /renewals
# ============================================================

@router.get(
    "",
    response_model=list[RenewalOut]
)
def get_all_renewals(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    renewals = db.query(Renewal).all()

    return renewals


# ============================================================
# UPCOMING RENEWALS
# GET /renewals/upcoming/list
# ============================================================

@router.get(
    "/upcoming/list",
    response_model=list[RenewalOut]
)
def get_upcoming_renewals(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    today = date.today()

    renewals = db.query(Renewal).filter(
        Renewal.status == "Upcoming",
        Renewal.previous_expiry_date >= today
    ).all()

    return renewals


# ============================================================
# EXPIRED RENEWALS
# GET /renewals/expired/list
# ============================================================

@router.get(
    "/expired/list",
    response_model=list[RenewalOut]
)
def get_expired_renewals(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    today = date.today()

    renewals = db.query(Renewal).filter(
        Renewal.status == "Expired",
        Renewal.previous_expiry_date < today
    ).all()

    return renewals


# ============================================================
# UPCOMING CONTRACT EXPIRIES
# GET /renewals/upcoming-contracts
# ============================================================

@router.get(
    "/upcoming-contracts"
)
def get_upcoming_contracts(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Only allow 30, 60, or 90 days
    if days not in [30, 60, 90]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Days must be 30, 60, or 90"
        )

    today = date.today()
    future_date = today + timedelta(days=days)

    contracts = db.query(Contract).filter(
        Contract.end_date >= today,
        Contract.end_date <= future_date,
        Contract.status != "Expired"
    ).all()

    return contracts


# ============================================================
# GET RENEWALS FOR A CONTRACT
# GET /renewals/contracts/{contract_id}/renewals
# ============================================================

@router.get(
    "/contracts/{contract_id}/renewals",
    response_model=list[RenewalOut]
)
def get_contract_renewals(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Check contract exists
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    renewals = db.query(Renewal).filter(
        Renewal.contract_id == contract_id
    ).all()

    return renewals


# ============================================================
# GET RENEWAL BY ID
# GET /renewals/{renewal_id}
# ============================================================

@router.get(
    "/{renewal_id}",
    response_model=RenewalOut
)
def get_renewal(
    renewal_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found"
        )

    return renewal


# ============================================================
# UPDATE RENEWAL
# PUT /renewals/{renewal_id}
# ============================================================

@router.put(
    "/{renewal_id}",
    response_model=RenewalOut
)
def update_renewal(
    renewal_id: int,
    renewal_data: RenewalUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found"
        )

    # Update renewal date
    if renewal_data.renewal_date is not None:
        renewal.renewal_date = renewal_data.renewal_date

    # Update new expiry date
    if renewal_data.new_expiry_date is not None:
        renewal.new_expiry_date = renewal_data.new_expiry_date

    # Update assigned user
    if renewal_data.assigned_to is not None:

        user = db.query(User).filter(
            User.id == renewal_data.assigned_to
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found"
            )

        renewal.assigned_to = renewal_data.assigned_to

    # Update notes
    if renewal_data.notes is not None:
        renewal.notes = renewal_data.notes

    # Validate date range
    if (
        renewal.renewal_date is not None
        and renewal.new_expiry_date is not None
        and renewal.new_expiry_date < renewal.renewal_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New expiry date cannot be earlier than renewal date"
        )

    db.commit()
    db.refresh(renewal)

    return renewal


# ============================================================
# UPDATE RENEWAL STATUS
# PATCH /renewals/{renewal_id}/status
# ============================================================

@router.patch(
    "/{renewal_id}/status",
    response_model=RenewalOut
)
def update_renewal_status(
    renewal_id: int,
    status_data: RenewalStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found"
        )

    allowed_statuses = [
        "Upcoming",
        "In Progress",
        "Renewed",
        "Expired",
        "Cancelled"
    ]

    if status_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid renewal status"
        )

    # Valid lifecycle transitions
    valid_transitions = {
        "Upcoming": [
            "In Progress",
            "Expired",
            "Cancelled"
        ],
        "In Progress": [
            "Renewed",
            "Cancelled"
        ],
        "Renewed": [],
        "Expired": [],
        "Cancelled": []
    }

    current_status = renewal.status
    new_status = status_data.status

    if new_status not in valid_transitions.get(
        current_status,
        []
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid status transition "
                f"from {current_status} to {new_status}"
            )
        )

    renewal.status = new_status

    db.commit()
    db.refresh(renewal)

    return renewal


# ============================================================
# COMPLETE RENEWAL
# POST /renewals/{renewal_id}/renew
# ============================================================

@router.post(
    "/{renewal_id}/renew",
    response_model=RenewalOut
)
def complete_renewal(
    renewal_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found"
        )

    # Renewal must be In Progress
    if renewal.status != "In Progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Renewal must be In Progress "
                "before it can be completed"
            )
        )

    # New expiry date required
    if renewal.new_expiry_date is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New expiry date is required"
        )

    # Find associated contract
    contract = db.query(Contract).filter(
        Contract.id == renewal.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Mark renewal as Renewed
    renewal.status = "Renewed"

    # Update contract expiry date
    contract.end_date = renewal.new_expiry_date

    db.commit()
    db.refresh(renewal)

    return renewal