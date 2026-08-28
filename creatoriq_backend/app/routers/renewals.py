from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.renewal import Renewal
from app.models.user import User
from app.schemas.renewal import (
    RenewalCreate,
    RenewalUpdate,
    RenewalStatusUpdate,
    RenewalComplete,
    RenewalResponse,
)
from app.core.dependencies import get_current_user, require_permission
from app.schemas.permissions import Permission


router = APIRouter(
    prefix="/renewals",
    tags=["Renewals"]
)


# ============================================================
# Helper: Get Renewal or 404
# ============================================================

def get_renewal_or_404(
    renewal_id: int,
    db: Session
):
    renewal = (
        db.query(Renewal)
        .filter(Renewal.id == renewal_id)
        .first()
    )

    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Renewal with ID {renewal_id} not found"
        )

    return renewal


# ============================================================
# 1. POST - Create Renewal
# ============================================================

@router.post(
    "",
    response_model=RenewalResponse,
    status_code=status.HTTP_201_CREATED
)
def create_renewal(
    renewal_data: RenewalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.MANAGE_RENEWALS)
    )
):
    # --------------------------------------------------------
    # Check contract
    # --------------------------------------------------------

    contract = (
        db.query(Contract)
        .filter(Contract.id == renewal_data.contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Contract with ID "
                f"{renewal_data.contract_id} not found"
            )
        )

    # --------------------------------------------------------
    # Check assigned user
    # --------------------------------------------------------

    assigned_user = (
        db.query(User)
        .filter(User.id == renewal_data.assigned_to)
        .first()
    )

    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"User with ID "
                f"{renewal_data.assigned_to} not found"
            )
        )

    # --------------------------------------------------------
    # Validate previous expiry date
    # --------------------------------------------------------

    if contract.end_date is not None:
        if renewal_data.previous_expiry_date != contract.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Previous expiry date must match "
                    "the contract expiry date"
                )
            )

    # --------------------------------------------------------
    # Validate renewal date
    # --------------------------------------------------------

    if (
        renewal_data.renewal_date
        < renewal_data.previous_expiry_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Renewal date cannot be earlier than "
                "the previous expiry date"
            )
        )

    # --------------------------------------------------------
    # Validate new expiry date
    # --------------------------------------------------------

    if (
        renewal_data.new_expiry_date
        < renewal_data.renewal_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "New expiry date cannot be earlier "
                "than renewal date"
            )
        )

    # --------------------------------------------------------
    # Create renewal
    # --------------------------------------------------------

    renewal = Renewal(
        contract_id=renewal_data.contract_id,
        renewal_date=renewal_data.renewal_date,
        previous_expiry_date=renewal_data.previous_expiry_date,
        new_expiry_date=renewal_data.new_expiry_date,
        assigned_to=renewal_data.assigned_to,
        notes=renewal_data.notes,
        status="Upcoming",
        approval_status=None
    )

    db.add(renewal)
    db.commit()
    db.refresh(renewal)

    return renewal


# ============================================================
# 2. GET - Get All Renewals
# ============================================================

@router.get(
    "",
    response_model=list[RenewalResponse],
    status_code=status.HTTP_200_OK
)
def get_renewals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Renewal)
        .order_by(Renewal.id.desc())
        .all()
    )


# ============================================================
# 3. GET - Upcoming Renewals
# IMPORTANT:
# This route must come BEFORE /{renewal_id}
# ============================================================

@router.get(
    "/upcoming",
    response_model=list[RenewalResponse],
    status_code=status.HTTP_200_OK
)
def get_upcoming_renewals(
    days: int = 90,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Days must be greater than zero"
        )

    today = date.today()
    future_date = today + timedelta(days=days)

    return (
        db.query(Renewal)
        .filter(
            Renewal.status == "Upcoming",
            Renewal.previous_expiry_date >= today,
            Renewal.previous_expiry_date <= future_date
        )
        .order_by(Renewal.previous_expiry_date.asc())
        .all()
    )


# ============================================================
# 4. GET - Expired Renewals
# IMPORTANT:
# This route must come BEFORE /{renewal_id}
# ============================================================

@router.get(
    "/expired",
    response_model=list[RenewalResponse],
    status_code=status.HTTP_200_OK
)
def get_expired_renewals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()

    return (
        db.query(Renewal)
        .filter(
            Renewal.previous_expiry_date < today,
            Renewal.status == "Upcoming"
        )
        .order_by(Renewal.previous_expiry_date.asc())
        .all()
    )


# ============================================================
# 5. GET - Get Renewal by ID
# IMPORTANT:
# This comes AFTER /upcoming and /expired
# ============================================================

@router.get(
    "/{renewal_id}",
    response_model=RenewalResponse,
    status_code=status.HTTP_200_OK
)
def get_renewal(
    renewal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_renewal_or_404(
        renewal_id,
        db
    )


# ============================================================
# 6. GET - Get Renewals for Contract
# Existing endpoint - kept unchanged
# ============================================================

@router.get(
    "/contract/{contract_id}",
    response_model=list[RenewalResponse],
    status_code=status.HTTP_200_OK
)
def get_contract_renewals(
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
            detail=f"Contract with ID {contract_id} not found"
        )

    return (
        db.query(Renewal)
        .filter(Renewal.contract_id == contract_id)
        .order_by(Renewal.id.asc())
        .all()
    )


# ============================================================
# 7. PUT - Update Renewal
# ============================================================

@router.put(
    "/{renewal_id}",
    response_model=RenewalResponse,
    status_code=status.HTTP_200_OK
)
def update_renewal(
    renewal_id: int,
    renewal_data: RenewalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.MANAGE_RENEWALS)
    )
):
    renewal = get_renewal_or_404(
        renewal_id,
        db
    )

    # --------------------------------------------------------
    # Validate assigned user
    # --------------------------------------------------------

    if renewal_data.assigned_to is not None:

        assigned_user = (
            db.query(User)
            .filter(User.id == renewal_data.assigned_to)
            .first()
        )

        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"User with ID "
                    f"{renewal_data.assigned_to} not found"
                )
            )

        renewal.assigned_to = renewal_data.assigned_to

    # --------------------------------------------------------
    # Determine final values
    # --------------------------------------------------------

    final_renewal_date = (
        renewal_data.renewal_date
        if renewal_data.renewal_date is not None
        else renewal.renewal_date
    )

    final_new_expiry_date = (
        renewal_data.new_expiry_date
        if renewal_data.new_expiry_date is not None
        else renewal.new_expiry_date
    )

    # --------------------------------------------------------
    # Validate date range
    # --------------------------------------------------------

    if final_new_expiry_date < final_renewal_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "New expiry date cannot be earlier "
                "than renewal date"
            )
        )

    # --------------------------------------------------------
    # Update fields
    # --------------------------------------------------------

    if renewal_data.renewal_date is not None:
        renewal.renewal_date = renewal_data.renewal_date

    if renewal_data.new_expiry_date is not None:
        renewal.new_expiry_date = renewal_data.new_expiry_date

    if renewal_data.notes is not None:
        renewal.notes = renewal_data.notes

    renewal.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(renewal)

    return renewal


# ============================================================
# 8. PATCH - Update Renewal Status
# ============================================================

@router.patch(
    "/{renewal_id}/status",
    response_model=RenewalResponse,
    status_code=status.HTTP_200_OK
)
def update_renewal_status(
    renewal_id: int,
    status_data: RenewalStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.MANAGE_RENEWALS)
    )
):
    renewal = get_renewal_or_404(
        renewal_id,
        db
    )

    allowed_statuses = {
        "Upcoming",
        "In Progress",
        "Renewed",
        "Expired",
        "Cancelled"
    }

    new_status = status_data.status

    # --------------------------------------------------------
    # Validate status value
    # --------------------------------------------------------

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid renewal status. Supported statuses: "
                "Upcoming, In Progress, Renewed, Expired, "
                "Cancelled"
            )
        )

    current_status = renewal.status

    # --------------------------------------------------------
    # Valid lifecycle transitions
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Update status
    # --------------------------------------------------------

    renewal.status = new_status
    renewal.updated_at = datetime.utcnow()

    # If manually marked expired, keep the renewal date/history.
    # No contract expiry update is performed.

    db.commit()
    db.refresh(renewal)

    return renewal


# ============================================================
# 9. POST - Complete Renewal
# ============================================================

@router.post(
    "/{renewal_id}/renew",
    response_model=RenewalResponse,
    status_code=status.HTTP_200_OK
)
def complete_renewal(
    renewal_id: int,
    renewal_data: RenewalComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(Permission.MANAGE_RENEWALS)
    )
):
    renewal = get_renewal_or_404(
        renewal_id,
        db
    )

    # --------------------------------------------------------
    # Renewal must currently be In Progress
    # --------------------------------------------------------

    if renewal.status != "In Progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only renewals with 'In Progress' status "
                "can be completed"
            )
        )

    # --------------------------------------------------------
    # Validate new expiry date
    # --------------------------------------------------------

    if renewal_data.new_expiry_date < renewal.renewal_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "New expiry date cannot be earlier "
                "than renewal date"
            )
        )

    # --------------------------------------------------------
    # Get contract
    # --------------------------------------------------------

    contract = (
        db.query(Contract)
        .filter(Contract.id == renewal.contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Contract with ID "
                f"{renewal.contract_id} not found"
            )
        )

    # --------------------------------------------------------
    # Update renewal
    # --------------------------------------------------------

    renewal.new_expiry_date = (
        renewal_data.new_expiry_date
    )

    renewal.status = "Renewed"
    renewal.updated_at = datetime.utcnow()

    # --------------------------------------------------------
    # Update contract expiry date
    # --------------------------------------------------------

    contract.end_date = renewal_data.new_expiry_date

    # If your contract workflow uses a specific active status,
    # preserve the existing status rather than changing it here.

    db.commit()
    db.refresh(renewal)

    return renewal