from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.renewal import Renewal
from app.models.contract import Contract
from app.models.user import User
from app.services.notification_service import NotificationService

from app.schemas.renewal import (
    RenewalCreate,
    RenewalUpdate,
    RenewalStatusUpdate,
    RenewalComplete,
    RenewalResponse,
)

from app.routers.dependencies import get_current_user


router = APIRouter(
    tags=["Renewals"]
)


# ============================================================
# HELPER - CHECK RENEWAL MANAGEMENT PERMISSION
# ============================================================
def check_renewal_permission(current_user: User):
    allowed_roles = {
        "Administrator",
        "Legal Manager",
        "Compliance Officer",
        "Contract Manager",
        "Department Head",
    }

    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage renewals"
        )


# ============================================================
# CREATE RENEWAL
# POST /renewals
# ============================================================
@router.post(
    "/renewals",
    response_model=RenewalResponse,
    status_code=status.HTTP_201_CREATED
)
def create_renewal(
    renewal_data: RenewalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_renewal_permission(current_user)

    # Verify contract
    contract = db.query(Contract).filter(
        Contract.id == renewal_data.contract_id
    ).first()

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Verify assigned user if provided
    if renewal_data.assigned_to is not None:
        assigned_user = db.query(User).filter(
            User.id == renewal_data.assigned_to
        ).first()

        if assigned_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found"
            )

    # Validate previous expiry date
    if renewal_data.previous_expiry_date != contract.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Previous expiry date must match the current "
                "contract expiry date"
            )
        )

    # Create renewal
    renewal = Renewal(
        contract_id=renewal_data.contract_id,
        renewal_date=renewal_data.renewal_date,
        previous_expiry_date=renewal_data.previous_expiry_date,
        new_expiry_date=renewal_data.new_expiry_date,
        status="Upcoming",
        assigned_to=renewal_data.assigned_to,
        notes=renewal_data.notes,
    )

    db.add(renewal)
    db.commit()
    db.refresh(renewal)

# Create renewal reminder notification
    if renewal.assigned_to is not None:
        NotificationService.create_renewal_reminder(
        db=db,
        user_id=renewal.assigned_to,
        contract_id=renewal.contract_id,
        message=(
            f"Contract {renewal.contract_id} renewal is scheduled for "
            f"{renewal.renewal_date}."
        )
    )

    return renewal

# ============================================================
# GET ALL RENEWALS
# GET /renewals
# ============================================================
@router.get(
    "/renewals",
    response_model=list[RenewalResponse]
)
def get_renewals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Renewal).all()


# ============================================================
# GET UPCOMING RENEWALS
# GET /renewals/upcoming
#
# Default threshold = 90 days
# ============================================================
@router.get(
    "/renewals/upcoming",
    response_model=list[RenewalResponse]
)
def get_upcoming_renewals(
    days: int = 90,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Days must be greater than 0"
        )

    today = date.today()
    threshold_date = date.fromordinal(
        today.toordinal() + days
    )

    renewals = db.query(Renewal).join(
        Contract,
        Renewal.contract_id == Contract.id
    ).filter(
        Contract.end_date >= today,
        Contract.end_date <= threshold_date,
        Renewal.status.in_(["Upcoming", "In Progress"])
    ).all()

    return renewals


# ============================================================
# GET EXPIRED RENEWALS
# GET /renewals/expired
# ============================================================
@router.get(
    "/renewals/expired",
    response_model=list[RenewalResponse]
)
def get_expired_renewals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()

    renewals = db.query(Renewal).join(
        Contract,
        Renewal.contract_id == Contract.id
    ).filter(
        Contract.end_date < today,
        Renewal.status.in_(["Upcoming", "In Progress", "Expired"])
    ).all()

    # Automatically mark expired renewals
    for renewal in renewals:
        if renewal.status in ["Upcoming", "In Progress"]:
            renewal.status = "Expired"
            renewal.updated_at = datetime.now(timezone.utc)

    db.commit()

    return renewals


# ============================================================
# GET RENEWAL BY ID
# IMPORTANT:
# This must remain AFTER /upcoming and /expired
# ============================================================
@router.get(
    "/renewals/{renewal_id}",
    response_model=RenewalResponse
)
def get_renewal(
    renewal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if renewal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found"
        )

    return renewal


# ============================================================
# GET RENEWALS FOR CONTRACT
# GET /contracts/{contract_id}/renewals
# ============================================================
@router.get(
    "/contracts/{contract_id}/renewals",
    response_model=list[RenewalResponse]
)
def get_contract_renewals(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return db.query(Renewal).filter(
        Renewal.contract_id == contract_id
    ).order_by(
        Renewal.created_at.desc()
    ).all()


# ============================================================
# UPDATE RENEWAL
# PUT /renewals/{renewal_id}
# ============================================================
@router.put(
    "/renewals/{renewal_id}",
    response_model=RenewalResponse
)
def update_renewal(
    renewal_id: int,
    renewal_data: RenewalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_renewal_permission(current_user)

    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if renewal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found"
        )

    update_data = renewal_data.model_dump(
        exclude_unset=True
    )

    # Validate assigned user
    if "assigned_to" in update_data:
        if update_data["assigned_to"] is not None:
            assigned_user = db.query(User).filter(
                User.id == update_data["assigned_to"]
            ).first()

            if assigned_user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assigned user not found"
                )

    # Validate date range using existing values when necessary
    renewal_date = update_data.get(
        "renewal_date",
        renewal.renewal_date
    )

    new_expiry_date = update_data.get(
        "new_expiry_date",
        renewal.new_expiry_date
    )

    if (
        renewal_date
        and new_expiry_date
        and new_expiry_date < renewal_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New expiry date cannot be earlier than renewal date"
        )

    for field, value in update_data.items():
        setattr(renewal, field, value)

    renewal.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(renewal)

    return renewal


# ============================================================
# UPDATE RENEWAL STATUS
# PATCH /renewals/{renewal_id}/status
# ============================================================
@router.patch(
    "/renewals/{renewal_id}/status",
    response_model=RenewalResponse
)
def update_renewal_status(
    renewal_id: int,
    status_data: RenewalStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_renewal_permission(current_user)

    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if renewal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found"
        )

    allowed_transitions = {
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
        "Cancelled": set(),
    }

    current_status = renewal.status
    requested_status = status_data.status

    if requested_status == current_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Renewal is already in this status"
        )

    if requested_status not in allowed_transitions.get(
        current_status,
        set()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid renewal status transition: "
                f"{current_status} -> {requested_status}"
            )
        )

    renewal.status = requested_status
    renewal.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(renewal)

    return renewal


# ============================================================
# COMPLETE RENEWAL
# POST /renewals/{renewal_id}/renew
# ============================================================
@router.post(
    "/renewals/{renewal_id}/renew",
    response_model=RenewalResponse
)
def complete_renewal(
    renewal_id: int,
    renewal_data: RenewalComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_renewal_permission(current_user)

    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if renewal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found"
        )

    # Renewal must be in progress
    if renewal.status != "In Progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only an In Progress renewal can be completed"
            )
        )

    contract = db.query(Contract).filter(
        Contract.id == renewal.contract_id
    ).first()

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated contract not found"
        )

    # Use supplied values or existing renewal values
    renewal_date = (
        renewal_data.renewal_date
        or renewal.renewal_date
        or date.today()
    )

    new_expiry_date = (
        renewal_data.new_expiry_date
        or renewal.new_expiry_date
    )

    if new_expiry_date is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New expiry date is required to complete renewal"
        )

    if new_expiry_date < renewal_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New expiry date cannot be earlier than renewal date"
        )

    # Update renewal
    renewal.renewal_date = renewal_date
    renewal.new_expiry_date = new_expiry_date
    renewal.status = "Renewed"
    renewal.updated_at = datetime.now(timezone.utc)

    # Update associated contract expiry
    contract.end_date = new_expiry_date

    # A successfully renewed contract becomes active
    contract.status = "Active"
    contract.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(renewal)

    return renewal