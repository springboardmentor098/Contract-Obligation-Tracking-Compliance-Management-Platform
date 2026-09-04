from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
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
    UpcomingRenewalResponse,
)
from app.core.security import get_current_user

router = APIRouter(
    prefix="/renewals",
    tags=["Renewals"],
)


# ---------------------------------------------------------
# STATUS TRANSITIONS
# ---------------------------------------------------------

ALLOWED_STATUS_TRANSITIONS = {
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


# ---------------------------------------------------------
# AUTHORIZATION HELPERS
# ---------------------------------------------------------

MANAGER_ROLES = {
    "admin",
    "manager",
    "contract_manager",
    "Admin",
    "Manager",
    "Contract Manager",
}


def is_manager(user: User) -> bool:
    return getattr(user, "role", None) in MANAGER_ROLES


def can_modify_renewal(
    current_user: User,
    renewal: Renewal,
) -> bool:

    if is_manager(current_user):
        return True

    if renewal.assigned_to == current_user.id:
        return True

    return False


# ---------------------------------------------------------
# GET RENEWAL
# ---------------------------------------------------------

def get_renewal_or_404(
    db: Session,
    renewal_id: int,
) -> Renewal:

    renewal = (
        db.query(Renewal)
        .filter(Renewal.id == renewal_id)
        .first()
    )

    if not renewal:
        raise HTTPException(
            status_code=404,
            detail="Renewal not found",
        )

    return renewal


# ---------------------------------------------------------
# GET CONTRACT
# ---------------------------------------------------------

def get_contract_or_404(
    db: Session,
    contract_id: int,
) -> Contract:

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

    return contract


# ---------------------------------------------------------
# POST /renewals
# ---------------------------------------------------------

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

    contract = get_contract_or_404(
        db,
        renewal_data.contract_id,
    )

    # Check assigned user
    if renewal_data.assigned_to is not None:

        assigned_user = (
            db.query(User)
            .filter(User.id == renewal_data.assigned_to)
            .first()
        )

        if not assigned_user:
            raise HTTPException(
                status_code=404,
                detail="Assigned user not found",
            )

    # Validate previous expiry against contract
    if hasattr(contract, "end_date"):

        if contract.end_date != renewal_data.previous_expiry_date:

            raise HTTPException(
                status_code=400,
                detail=(
                    "previous_expiry_date does not match "
                    "the contract expiry date"
                ),
            )

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

    return renewal


# ---------------------------------------------------------
# GET /renewals
# ---------------------------------------------------------

@router.get(
    "",
    response_model=list[RenewalResponse],
)
def get_all_renewals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    query = db.query(Renewal)

    # Managers can see everything.
    # Normal users see assigned renewals.
    if not is_manager(current_user):
        query = query.filter(
            Renewal.assigned_to == current_user.id
        )

    renewals = (
        query
        .order_by(Renewal.previous_expiry_date.asc())
        .all()
    )

    return renewals


# ---------------------------------------------------------
# GET /renewals/upcoming
# IMPORTANT: This must be before /{renewal_id}
# ---------------------------------------------------------

@router.get(
    "/upcoming",
    response_model=list[UpcomingRenewalResponse],
)
def get_upcoming_renewals(
    days: int = Query(
        default=30,
        ge=1,
        le=365,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    today = date.today()

    contracts = db.query(Contract).all()

    results = []

    for contract in contracts:

        if not hasattr(contract, "end_date"):
            continue

        expiry_date = contract.end_date

        if expiry_date is None:
            continue

        days_remaining = (
            expiry_date - today
        ).days

        if 0 <= days_remaining <= days:

            renewal = (
                db.query(Renewal)
                .filter(
                    Renewal.contract_id == contract.id,
                    Renewal.status.notin_(
                        ["Renewed", "Cancelled"]
                    ),
                )
                .order_by(
                    Renewal.created_at.desc()
                )
                .first()
            )

            # Normal users only see their assignments
            if (
                not is_manager(current_user)
                and renewal
                and renewal.assigned_to != current_user.id
            ):
                continue

            results.append(
                UpcomingRenewalResponse(
                    contract_id=contract.id,
                    renewal_id=renewal.id if renewal else None,
                    expiry_date=expiry_date,
                    days_remaining=days_remaining,
                    status=(
                        renewal.status
                        if renewal
                        else "Upcoming"
                    ),
                )
            )

    results.sort(
        key=lambda x: x.days_remaining
    )

    return results


# ---------------------------------------------------------
# GET /renewals/expired
# ---------------------------------------------------------

@router.get(
    "/expired",
    response_model=list[UpcomingRenewalResponse],
)
def get_expired_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    today = date.today()

    contracts = db.query(Contract).all()

    results = []

    for contract in contracts:

        if not hasattr(contract, "end_date"):
            continue

        expiry_date = contract.end_date

        if expiry_date is None:
            continue

        if expiry_date < today:

            renewal = (
                db.query(Renewal)
                .filter(
                    Renewal.contract_id == contract.id,
                    Renewal.status.notin_(
                        ["Renewed", "Cancelled"]
                    ),
                )
                .order_by(
                    Renewal.created_at.desc()
                )
                .first()
            )

            # Do not report a contract as expired if
            # its active renewal already extended it.
            if renewal and renewal.status == "Renewed":
                continue

            if (
                not is_manager(current_user)
                and renewal
                and renewal.assigned_to != current_user.id
            ):
                continue

            results.append(
                UpcomingRenewalResponse(
                    contract_id=contract.id,
                    renewal_id=renewal.id if renewal else None,
                    expiry_date=expiry_date,
                    days_remaining=(
                        expiry_date - today
                    ).days,
                    status=(
                        renewal.status
                        if renewal
                        else "Expired"
                    ),
                )
            )

    return results


# ---------------------------------------------------------
# GET /renewals/{renewal_id}
# ---------------------------------------------------------

@router.get(
    "/{renewal_id}",
    response_model=RenewalResponse,
)
def get_renewal(
    renewal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    renewal = get_renewal_or_404(
        db,
        renewal_id,
    )

    if (
        not is_manager(current_user)
        and renewal.assigned_to != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to view this renewal",
        )

    return renewal


# ---------------------------------------------------------
# GET /contracts/{contract_id}/renewals
# This route belongs to renewal functionality but uses
# /contracts prefix as required by Sprint 10.
# ---------------------------------------------------------

@router.get(
    "/contract/{contract_id}",
    response_model=list[RenewalResponse],
)
def get_contract_renewals_internal(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    get_contract_or_404(
        db,
        contract_id,
    )

    query = db.query(Renewal).filter(
        Renewal.contract_id == contract_id
    )

    if not is_manager(current_user):

        query = query.filter(
            Renewal.assigned_to == current_user.id
        )

    return (
        query
        .order_by(
            Renewal.created_at.desc()
        )
        .all()
    )


# ---------------------------------------------------------
# PUT /renewals/{renewal_id}
# ---------------------------------------------------------

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

    renewal = get_renewal_or_404(
        db,
        renewal_id,
    )

    if not can_modify_renewal(
        current_user,
        renewal,
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to modify this renewal",
        )

    # Assigned user validation
    if renewal_data.assigned_to is not None:

        assigned_user = (
            db.query(User)
            .filter(
                User.id == renewal_data.assigned_to
            )
            .first()
        )

        if not assigned_user:
            raise HTTPException(
                status_code=404,
                detail="Assigned user not found",
            )

    update_data = renewal_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():

        if field == "assigned_to":
            if not is_manager(current_user):
                raise HTTPException(
                    status_code=403,
                    detail="Only managers can assign renewal responsibility",
                )

        setattr(
            renewal,
            field,
            value,
        )

    # Final date validation
    if (
        renewal.new_expiry_date
        and renewal.renewal_date
        and renewal.new_expiry_date
        < renewal.renewal_date
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "new_expiry_date cannot be earlier "
                "than renewal_date"
            ),
        )

    db.commit()
    db.refresh(renewal)

    return renewal


# ---------------------------------------------------------
# PATCH /renewals/{renewal_id}/status
# ---------------------------------------------------------

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

    renewal = get_renewal_or_404(
        db,
        renewal_id,
    )

    if not can_modify_renewal(
        current_user,
        renewal,
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to update this renewal",
        )

    current_status = renewal.status
    new_status = status_data.status

    allowed = ALLOWED_STATUS_TRANSITIONS.get(
        current_status,
        set(),
    )

    if new_status not in allowed:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid renewal status transition: "
                f"{current_status} -> {new_status}"
            ),
        )

    renewal.status = new_status

    db.commit()
    db.refresh(renewal)

    return renewal


# ---------------------------------------------------------
# POST /renewals/{renewal_id}/renew
# ---------------------------------------------------------

@router.post(
    "/{renewal_id}/renew",
    response_model=RenewalResponse,
)
def complete_renewal(
    renewal_id: int,
    renewal_data: RenewalComplete | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    renewal = get_renewal_or_404(
        db,
        renewal_id,
    )

    if not can_modify_renewal(
        current_user,
        renewal,
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to complete this renewal",
        )

    if renewal.status != "In Progress":

        raise HTTPException(
            status_code=400,
            detail=(
                "Only an In Progress renewal "
                "can be completed"
            ),
        )

    if renewal_data:

        if renewal_data.new_expiry_date:
            renewal.new_expiry_date = (
                renewal_data.new_expiry_date
            )

        if renewal_data.notes:
            renewal.notes = renewal_data.notes

    if renewal.new_expiry_date is None:

        raise HTTPException(
            status_code=400,
            detail=(
                "new_expiry_date is required "
                "to complete the renewal"
            ),
        )

    if (
        renewal.renewal_date
        and renewal.new_expiry_date
        < renewal.renewal_date
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "new_expiry_date cannot be earlier "
                "than renewal_date"
            ),
        )

    # Mark renewal completed
    renewal.status = "Renewed"

    # Update contract expiry
    contract = get_contract_or_404(
        db,
        renewal.contract_id,
    )

    if hasattr(contract, "end_date"):
        contract.end_date = renewal.new_expiry_date

    # If your Contract model uses expiry_date instead,
    # replace the above with:
    #
    # contract.expiry_date = renewal.new_expiry_date

    if renewal.renewal_date is None:
        renewal.renewal_date = date.today()

    db.commit()
    db.refresh(renewal)

    return renewal