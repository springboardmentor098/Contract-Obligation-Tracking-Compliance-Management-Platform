from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.renewal import Renewal
from app.models.user import User
from app.schemas.renewal import (
    RenewalComplete,
    RenewalCreate,
    RenewalResponse,
    RenewalStatusUpdate,
    RenewalUpdate,
)
from app.api.dependencies import get_current_user


router = APIRouter(
    prefix="/renewals",
    tags=["Renewals"],
)


# ============================================================
# Helper Functions
# ============================================================

def get_renewal_or_404(
    renewal_id: UUID,
    db: Session,
) -> Renewal:
    renewal = db.get(Renewal, renewal_id)

    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found",
        )

    return renewal


def get_contract_or_404(
    contract_id: UUID,
    db: Session,
) -> Contract:
    contract = db.get(Contract, contract_id)

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    return contract


def get_user_or_404(
    user_id: UUID,
    db: Session,
) -> User:
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assigned user is inactive",
        )

    return user


def check_contract_access(
    contract: Contract,
    current_user: User,
) -> None:
    """
    Admins can access all contracts.
    Other users can access contracts they created
    or are assigned to.
    """

    if current_user.role.lower() == "admin":
        return

    if contract.created_by == current_user.id:
        return

    if contract.assigned_to == current_user.id:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this contract",
    )


def check_renewal_access(
    renewal: Renewal,
    contract: Contract,
    current_user: User,
) -> None:
    """
    Authorization for renewal operations.

    Admin:
        Full access.

    Contract owner:
        Access.

    Contract assignee:
        Access.

    Renewal assignee:
        Access.
    """

    if current_user.role.lower() == "admin":
        return

    if contract.created_by == current_user.id:
        return

    if contract.assigned_to == current_user.id:
        return

    if renewal.assigned_to == current_user.id:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this renewal",
    )


def validate_dates(
    renewal_date: date | None,
    previous_expiry_date: date | None,
    new_expiry_date: date | None,
) -> None:

    if (
        renewal_date
        and previous_expiry_date
        and renewal_date > previous_expiry_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Renewal date cannot be later than previous expiry date",
        )

    if (
        renewal_date
        and new_expiry_date
        and new_expiry_date < renewal_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New expiry date cannot be earlier than renewal date",
        )


# ============================================================
# 1. CREATE RENEWAL
# POST /renewals
# ============================================================

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
        renewal_data.contract_id,
        db,
    )

    check_contract_access(
        contract,
        current_user,
    )

    get_user_or_404(
        renewal_data.assigned_to,
        db,
    )

    validate_dates(
        renewal_data.renewal_date,
        renewal_data.previous_expiry_date,
        renewal_data.new_expiry_date,
    )

    renewal = Renewal(
        contract_id=renewal_data.contract_id,
        assigned_to=renewal_data.assigned_to,
        previous_expiry_date=renewal_data.previous_expiry_date,
        renewal_date=renewal_data.renewal_date,
        new_expiry_date=renewal_data.new_expiry_date,
        status="Upcoming",
        notes=renewal_data.notes,
    )

    db.add(renewal)
    db.commit()
    db.refresh(renewal)

    return renewal


# ============================================================
# 2. GET ALL RENEWALS
# GET /renewals
# ============================================================

@router.get(
    "",
    response_model=list[RenewalResponse],
)
def get_all_renewals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Renewal)

    if current_user.role.lower() != "admin":
        query = (
            query
            .join(
                Contract,
                Renewal.contract_id == Contract.id,
            )
            .where(
                (Contract.created_by == current_user.id)
                | (Contract.assigned_to == current_user.id)
                | (Renewal.assigned_to == current_user.id)
            )
        )

    result = db.execute(query)

    return result.scalars().unique().all()


# ============================================================
# 3. GET RENEWAL BY ID
# GET /renewals/{renewal_id}
# ============================================================

@router.get(
    "/{renewal_id}",
    response_model=RenewalResponse,
)
def get_renewal(
    renewal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    renewal = get_renewal_or_404(
        renewal_id,
        db,
    )

    contract = get_contract_or_404(
        renewal.contract_id,
        db,
    )

    check_renewal_access(
        renewal,
        contract,
        current_user,
    )

    return renewal


# ============================================================
# 4. GET RENEWALS FOR CONTRACT
# GET /contracts/{contract_id}/renewals
# ============================================================

@router.get(
    "/contracts/{contract_id}/renewals",
    response_model=list[RenewalResponse],
)
def get_contract_renewals(
    contract_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contract = get_contract_or_404(
        contract_id,
        db,
    )

    check_contract_access(
        contract,
        current_user,
    )

    result = db.execute(
        select(Renewal)
        .where(Renewal.contract_id == contract_id)
        .order_by(Renewal.created_at.desc())
    )

    return result.scalars().all()


# ============================================================
# 5. UPDATE RENEWAL
# PUT /renewals/{renewal_id}
# ============================================================

@router.put(
    "/{renewal_id}",
    response_model=RenewalResponse,
)
def update_renewal(
    renewal_id: UUID,
    renewal_data: RenewalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    renewal = get_renewal_or_404(
        renewal_id,
        db,
    )

    contract = get_contract_or_404(
        renewal.contract_id,
        db,
    )

    check_renewal_access(
        renewal,
        contract,
        current_user,
    )

    update_data = renewal_data.model_dump(
        exclude_unset=True
    )

    if "assigned_to" in update_data:
        get_user_or_404(
            update_data["assigned_to"],
            db,
        )

    new_renewal_date = update_data.get(
        "renewal_date",
        renewal.renewal_date,
    )

    new_previous_expiry_date = update_data.get(
        "previous_expiry_date",
        renewal.previous_expiry_date,
    )

    new_expiry_date = update_data.get(
        "new_expiry_date",
        renewal.new_expiry_date,
    )

    validate_dates(
        new_renewal_date,
        new_previous_expiry_date,
        new_expiry_date,
    )

    for field, value in update_data.items():
        setattr(
            renewal,
            field,
            value,
        )

    db.commit()
    db.refresh(renewal)

    return renewal


# ============================================================
# 6. UPDATE RENEWAL STATUS
# PATCH /renewals/{renewal_id}/status
# ============================================================

@router.patch(
    "/{renewal_id}/status",
    response_model=RenewalResponse,
)
def update_renewal_status(
    renewal_id: UUID,
    status_data: RenewalStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    renewal = get_renewal_or_404(
        renewal_id,
        db,
    )

    contract = get_contract_or_404(
        renewal.contract_id,
        db,
    )

    check_renewal_access(
        renewal,
        contract,
        current_user,
    )

    allowed_statuses = {
        "Upcoming",
        "In Progress",
        "Renewed",
        "Expired",
        "Cancelled",
    }

    new_status = status_data.status.strip()

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid renewal status. "
                "Allowed statuses: Upcoming, In Progress, "
                "Renewed, Expired, Cancelled"
            ),
        )

    current_status = renewal.status

    valid_transitions = {
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

    if new_status != current_status:
        if new_status not in valid_transitions.get(
            current_status,
            set(),
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid renewal status transition: "
                    f"{current_status} -> {new_status}"
                ),
            )

    renewal.status = new_status

    db.commit()
    db.refresh(renewal)

    return renewal


# ============================================================
# 7. COMPLETE RENEWAL
# POST /renewals/{renewal_id}/renew
# ============================================================

@router.post(
    "/{renewal_id}/renew",
    response_model=RenewalResponse,
)
def complete_renewal(
    renewal_id: UUID,
    renewal_data: RenewalComplete | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    renewal = get_renewal_or_404(
        renewal_id,
        db,
    )

    contract = get_contract_or_404(
        renewal.contract_id,
        db,
    )

    check_renewal_access(
        renewal,
        contract,
        current_user,
    )

    if renewal.status != "In Progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only renewals with status "
                "'In Progress' can be completed"
            ),
        )

    if renewal_data is not None:
        update_data = renewal_data.model_dump(
            exclude_unset=True
        )

        if "new_expiry_date" in update_data:
            renewal.new_expiry_date = (
                update_data["new_expiry_date"]
            )

    if not renewal.new_expiry_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New expiry date is required to complete renewal",
        )

    if (
        renewal.renewal_date
        and renewal.new_expiry_date < renewal.renewal_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New expiry date cannot be earlier than renewal date",
        )

    renewal.status = "Renewed"

    # Update the contract's active expiry date.
    contract.end_date = renewal.new_expiry_date

    db.commit()
    db.refresh(renewal)

    return renewal


# ============================================================
# 8. UPCOMING RENEWALS
# GET /renewals/upcoming/list
# ============================================================

@router.get(
    "/upcoming/list",
    response_model=list[RenewalResponse],
)
def get_upcoming_renewals(
    days: int = Query(
        default=90,
        ge=1,
        le=365,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()

    expiry_limit = today.fromordinal(
        today.toordinal() + days
    )

    query = (
        select(Renewal)
        .join(
            Contract,
            Renewal.contract_id == Contract.id,
        )
        .where(
            Contract.end_date.is_not(None),
            Contract.end_date >= today,
            Contract.end_date <= expiry_limit,
            Renewal.status.in_(
                ["Upcoming", "In Progress"]
            ),
        )
        .order_by(Contract.end_date.asc())
    )

    if current_user.role.lower() != "admin":
        query = query.where(
            (Contract.created_by == current_user.id)
            | (Contract.assigned_to == current_user.id)
            | (Renewal.assigned_to == current_user.id)
        )

    result = db.execute(query)

    return result.scalars().unique().all()


# ============================================================
# 9. EXPIRED RENEWALS / CONTRACTS
# GET /renewals/expired/list
# ============================================================

@router.get(
    "/expired/list",
    response_model=list[RenewalResponse],
)
def get_expired_renewals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()

    query = (
        select(Renewal)
        .join(
            Contract,
            Renewal.contract_id == Contract.id,
        )
        .where(
            Contract.end_date.is_not(None),
            Contract.end_date < today,
            Renewal.status.in_(
                ["Upcoming", "In Progress"]
            ),
        )
        .order_by(Contract.end_date.asc())
    )

    if current_user.role.lower() != "admin":
        query = query.where(
            (Contract.created_by == current_user.id)
            | (Contract.assigned_to == current_user.id)
            | (Renewal.assigned_to == current_user.id)
        )

    result = db.execute(query)

    renewals = result.scalars().unique().all()

    # Mark qualifying renewals as expired.
    for renewal in renewals:
        renewal.status = "Expired"

    if renewals:
        db.commit()

        for renewal in renewals:
            db.refresh(renewal)

    return renewals