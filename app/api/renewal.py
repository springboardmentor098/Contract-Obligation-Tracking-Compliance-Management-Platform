from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.renewal import Renewal
from app.models.user import User
from app.schemas.renewal_schema import (
    RenewalCreate,
    RenewalUpdate,
    RenewalStatusUpdate,
    RenewalComplete,
    RenewalResponse,
    RENEWAL_STATUSES,
)
from app.middleware.auth import require_roles


router = APIRouter(
    prefix="/renewals",
    tags=["Renewals"]
)


# ============================================================
# ROLE DEFINITIONS
# ============================================================

ALL_ROLES = (
    "Administrator",
    "Legal Manager",
    "Compliance Officer",
    "Contract Manager",
    "Department Head",
    "Employee",
)

MANAGER_ROLES = (
    "Administrator",
    "Legal Manager",
    "Contract Manager",
)

STATUS_ROLES = (
    "Administrator",
    "Legal Manager",
    "Contract Manager",
)

RENEW_ROLES = (
    "Administrator",
    "Legal Manager",
    "Contract Manager",
)


# ============================================================
# CREATE RENEWAL
# POST /renewals
# ============================================================

@router.post(
    "",
    response_model=RenewalResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_roles(*MANAGER_ROLES))
    ]
)
def create_renewal(
    renewal_data: RenewalCreate,
    current_user: dict = Depends(
        require_roles(*MANAGER_ROLES)
    ),
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Verify contract exists
    # --------------------------------------------------------

    contract = db.query(Contract).filter(
        Contract.id == renewal_data.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # --------------------------------------------------------
    # Verify assigned user exists
    # --------------------------------------------------------

    if renewal_data.assigned_to is not None:

        assigned_user = db.query(User).filter(
            User.id == renewal_data.assigned_to
        ).first()

        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found"
            )

    # --------------------------------------------------------
    # Validate dates
    # --------------------------------------------------------

    if (
        renewal_data.new_expiry_date is not None
        and renewal_data.new_expiry_date < renewal_data.renewal_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New expiry date cannot be earlier than renewal date"
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
        status="Upcoming"
    )

    db.add(renewal)
    db.commit()
    db.refresh(renewal)

    return renewal


# ============================================================
# GET ALL RENEWALS
# GET /renewals
# ============================================================

@router.get(
    "",
    response_model=list[RenewalResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_roles(*ALL_ROLES))
    ]
)
def get_renewals(
    db: Session = Depends(get_db)
):

    renewals = db.query(Renewal).all()

    return renewals


# ============================================================
# GET UPCOMING RENEWALS
# GET /renewals/upcoming
#
# IMPORTANT:
# Uses CURRENT contract end_date.
# Renewal history cannot make a renewed contract appear
# as upcoming.
# ============================================================

@router.get(
    "/upcoming",
    response_model=list[RenewalResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_roles(*ALL_ROLES))
    ]
)
def get_upcoming_renewals(
    days: int = 90,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Validate days
    # --------------------------------------------------------

    if days <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Days must be greater than zero"
        )

    today = date.today()
    upcoming_date = today + timedelta(days=days)

    # --------------------------------------------------------
    # IMPORTANT:
    # Check CURRENT contract expiry date.
    #
    # Do NOT use Renewal.previous_expiry_date here because
    # that is historical renewal information.
    # --------------------------------------------------------

    renewals = (
        db.query(Renewal)
        .join(
            Contract,
            Renewal.contract_id == Contract.id
        )
        .filter(
            Contract.end_date >= today,
            Contract.end_date <= upcoming_date,
            Renewal.status.in_(
                ["Upcoming", "In Progress"]
            )
        )
        .all()
    )

    return renewals


# ============================================================
# GET EXPIRED RENEWALS
# GET /renewals/expired
#
# IMPORTANT:
# Uses CURRENT contract end_date.
# ============================================================

@router.get(
    "/expired",
    response_model=list[RenewalResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_roles(*ALL_ROLES))
    ]
)
def get_expired_renewals(
    db: Session = Depends(get_db)
):

    today = date.today()

    # --------------------------------------------------------
    # IMPORTANT:
    # Check CURRENT contract expiry date.
    #
    # An old Renewal.previous_expiry_date must NOT cause
    # the current contract to be considered expired.
    # --------------------------------------------------------

    renewals = (
        db.query(Renewal)
        .join(
            Contract,
            Renewal.contract_id == Contract.id
        )
        .filter(
            Contract.end_date < today,
            Renewal.status.in_(
                ["Upcoming", "In Progress"]
            )
        )
        .all()
    )

    return renewals


# ============================================================
# GET RENEWALS FOR CONTRACT
# GET /renewals/contract/{contract_id}
# ============================================================

@router.get(
    "/contract/{contract_id}",
    response_model=list[RenewalResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_roles(*ALL_ROLES))
    ]
)
def get_contract_renewals(
    contract_id: int,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Verify contract exists
    # --------------------------------------------------------

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
    response_model=RenewalResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_roles(*ALL_ROLES))
    ]
)
def get_renewal(
    renewal_id: int,
    db: Session = Depends(get_db)
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
    response_model=RenewalResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_roles(*MANAGER_ROLES))
    ]
)
def update_renewal(
    renewal_id: int,
    renewal_data: RenewalUpdate,
    db: Session = Depends(get_db)
):

    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found"
        )

    # --------------------------------------------------------
    # Verify assigned user
    # --------------------------------------------------------

    if renewal_data.assigned_to is not None:

        assigned_user = db.query(User).filter(
            User.id == renewal_data.assigned_to
        ).first()

        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found"
            )

    # --------------------------------------------------------
    # Validate dates
    # --------------------------------------------------------

    if (
        renewal_data.new_expiry_date is not None
        and renewal_data.renewal_date is not None
        and renewal_data.new_expiry_date
        < renewal_data.renewal_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New expiry date cannot be earlier than renewal date"
        )

    # --------------------------------------------------------
    # Update fields
    # --------------------------------------------------------

    if renewal_data.renewal_date is not None:
        renewal.renewal_date = renewal_data.renewal_date

    if renewal_data.new_expiry_date is not None:
        renewal.new_expiry_date = renewal_data.new_expiry_date

    if renewal_data.assigned_to is not None:
        renewal.assigned_to = renewal_data.assigned_to

    if renewal_data.notes is not None:
        renewal.notes = renewal_data.notes

    db.commit()
    db.refresh(renewal)

    return renewal


# ============================================================
# UPDATE RENEWAL STATUS
# PATCH /renewals/{renewal_id}/status
# ============================================================

@router.patch(
    "/{renewal_id}/status",
    response_model=RenewalResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_roles(*STATUS_ROLES))
    ]
)
def update_renewal_status(
    renewal_id: int,
    status_data: RenewalStatusUpdate,
    db: Session = Depends(get_db)
):

    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found"
        )

    # --------------------------------------------------------
    # Validate status
    # --------------------------------------------------------

    if status_data.status not in RENEWAL_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid renewal status"
        )

    current_status = renewal.status
    new_status = status_data.status

    # --------------------------------------------------------
    # Allowed workflow
    #
    # Upcoming → In Progress
    # In Progress → Renewed
    # Upcoming → Expired
    # Upcoming → Cancelled
    # In Progress → Cancelled
    # --------------------------------------------------------

    allowed_transitions = {
        "Upcoming": {
            "In Progress",
            "Expired",
            "Cancelled",
        },
        "In Progress": {
            "Renewed",
            "Cancelled",
        },
        "Renewed": set(),
        "Expired": set(),
        "Cancelled": set(),
    }

    if new_status not in allowed_transitions.get(
        current_status,
        set()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid renewal status transition: "
                f"{current_status} → {new_status}"
            )
        )

    renewal.status = new_status

    db.commit()
    db.refresh(renewal)

    return renewal


# ============================================================
# COMPLETE / RENEW CONTRACT
# POST /renewals/{renewal_id}/renew
# ============================================================

@router.post(
    "/{renewal_id}/renew",
    response_model=RenewalResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_roles(*RENEW_ROLES))
    ]
)
def complete_renewal(
    renewal_id: int,
    renewal_data: RenewalComplete,
    db: Session = Depends(get_db)
):

    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found"
        )

    # --------------------------------------------------------
    # Renewal must be In Progress
    # --------------------------------------------------------

    if renewal.status != "In Progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only an In Progress renewal "
                "can be completed"
            )
        )

    # --------------------------------------------------------
    # Validate new expiry date
    # --------------------------------------------------------

    if renewal_data.new_expiry_date < renewal.renewal_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New expiry date cannot be earlier than renewal date"
        )

    # --------------------------------------------------------
    # Update renewal
    # --------------------------------------------------------

    renewal.new_expiry_date = renewal_data.new_expiry_date
    renewal.status = "Renewed"

    # --------------------------------------------------------
    # Update associated contract expiry date
    # --------------------------------------------------------

    contract = db.query(Contract).filter(
        Contract.id == renewal.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated contract not found"
        )

    contract.end_date = renewal_data.new_expiry_date

    db.commit()
    db.refresh(renewal)

    return renewal