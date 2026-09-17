from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.renewal import Renewal
from app.models.user import User
from app.schemas.renewal import (
    RenewalCreate,
    RenewalResponse,
    RenewalMonitoringResponse,
    RenewalStatusUpdate,
    RenewalUpdate,
)
from app.utils.authorization import get_current_user


router = APIRouter(
    prefix="/renewals",
    tags=["Renewals"]
)


ALLOWED_STATUSES = {
    "Upcoming",
    "In Progress",
    "Renewed",
    "Expired",
    "Cancelled",
}


ALLOWED_TRANSITIONS = {
    "Upcoming": {"In Progress", "Expired", "Cancelled"},
    "In Progress": {"Renewed", "Cancelled"},
    "Renewed": set(),
    "Expired": set(),
    "Cancelled": set(),
}


MANAGER_ROLES = {
    "Administrator",
    "Legal Manager",
    "Contract Manager",
}


def require_manager(current_user: dict):
    role = current_user.get("role", "")

    if role not in MANAGER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this operation"
        )


def get_renewal_or_404(
    renewal_id: int,
    db: Session
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


def get_contract_or_404(
    contract_id: int,
    db: Session
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return contract


def get_user_or_404(
    user_id: int,
    db: Session
):
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assigned user is inactive"
        )

    return user


# ============================================================
# 1. CREATE RENEWAL
# ============================================================

@router.post(
    "",
    response_model=RenewalResponse,
    status_code=status.HTTP_201_CREATED
)
def create_renewal(
    renewal_data: RenewalCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_manager(current_user)

    contract = get_contract_or_404(
        renewal_data.contract_id,
        db
    )

    if renewal_data.assigned_to is not None:
        get_user_or_404(
            renewal_data.assigned_to,
            db
        )

    if (
        renewal_data.new_expiry_date is not None
        and renewal_data.new_expiry_date < renewal_data.previous_expiry_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="new_expiry_date cannot be earlier than previous_expiry_date"
        )

    renewal = Renewal(
        contract_id=contract.id,
        renewal_date=renewal_data.renewal_date,
        previous_expiry_date=renewal_data.previous_expiry_date,
        new_expiry_date=renewal_data.new_expiry_date,
        status="Upcoming",
        assigned_to=renewal_data.assigned_to,
        notes=renewal_data.notes,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        updated_at=datetime.now(timezone.utc).replace(tzinfo=None)
    )

    db.add(renewal)
    db.commit()
    db.refresh(renewal)

    return renewal


# ============================================================
# 2. GET ALL RENEWALS
# ============================================================

@router.get(
    "",
    response_model=list[RenewalResponse]
)
def get_renewals(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    renewals = db.query(Renewal).order_by(
        Renewal.id.desc()
    ).all()

    return renewals


# ============================================================
# 3. GET RENEWAL BY ID
# ============================================================

@router.get(
    "/{renewal_id}",
    response_model=RenewalResponse
)
def get_renewal(
    renewal_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_renewal_or_404(
        renewal_id,
        db
    )


# ============================================================
# 4. GET RENEWAL HISTORY FOR CONTRACT
# ============================================================

@router.get(
    "/contract/{contract_id}",
    response_model=list[RenewalResponse]
)
def get_contract_renewals(
    contract_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    get_contract_or_404(
        contract_id,
        db
    )

    return db.query(Renewal).filter(
        Renewal.contract_id == contract_id
    ).order_by(
        Renewal.id.asc()
    ).all()


# ============================================================
# 5. UPDATE RENEWAL
# ============================================================

@router.put(
    "/{renewal_id}",
    response_model=RenewalResponse
)
def update_renewal(
    renewal_id: int,
    renewal_data: RenewalUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_manager(current_user)

    renewal = get_renewal_or_404(
        renewal_id,
        db
    )

    if renewal.status == "Renewed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A completed renewal cannot be modified"
        )

    if renewal.status == "Cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A cancelled renewal cannot be modified"
        )

    if renewal_data.assigned_to is not None:
        get_user_or_404(
            renewal_data.assigned_to,
            db
        )
        renewal.assigned_to = renewal_data.assigned_to

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

    if (
        final_renewal_date is not None
        and final_new_expiry_date is not None
        and final_new_expiry_date < final_renewal_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="new_expiry_date cannot be earlier than renewal_date"
        )

    if renewal_data.renewal_date is not None:
        renewal.renewal_date = renewal_data.renewal_date

    if renewal_data.new_expiry_date is not None:
        renewal.new_expiry_date = renewal_data.new_expiry_date

    if renewal_data.notes is not None:
        renewal.notes = renewal_data.notes

    renewal.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    db.commit()
    db.refresh(renewal)

    return renewal


# ============================================================
# 6. UPDATE RENEWAL STATUS
# ============================================================

@router.patch(
    "/{renewal_id}/status",
    response_model=RenewalResponse
)
def update_renewal_status(
    renewal_id: int,
    status_data: RenewalStatusUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_manager(current_user)

    renewal = get_renewal_or_404(
        renewal_id,
        db
    )

    new_status = status_data.status

    if new_status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid renewal status. Allowed statuses: "
                "Upcoming, In Progress, Renewed, Expired, Cancelled"
            )
        )

    if new_status == renewal.status:
        return renewal

    allowed_next_statuses = ALLOWED_TRANSITIONS.get(
        renewal.status,
        set()
    )

    if new_status not in allowed_next_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid renewal status transition: "
                f"{renewal.status} -> {new_status}"
            )
        )

    renewal.status = new_status
    renewal.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    db.commit()
    db.refresh(renewal)

    return renewal


# ============================================================
# 7. COMPLETE RENEWAL
# ============================================================

@router.post(
    "/{renewal_id}/renew",
    response_model=RenewalResponse
)
def complete_renewal(
    renewal_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_manager(current_user)

    renewal = get_renewal_or_404(
        renewal_id,
        db
    )

    if renewal.status != "In Progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only an In Progress renewal can be completed"
        )

    if renewal.new_expiry_date is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="new_expiry_date is required to complete a renewal"
        )

    contract = get_contract_or_404(
        renewal.contract_id,
        db
    )

    if (
        renewal.renewal_date is not None
        and renewal.new_expiry_date < renewal.renewal_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="new_expiry_date cannot be earlier than renewal_date"
        )

    # Update the actual contract expiry date.
    contract.end_date = renewal.new_expiry_date

    # A successfully renewed contract becomes Active.
    contract.status = "Active"

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    contract.updated_at = now

    renewal.status = "Renewed"
    renewal.renewal_date = renewal.renewal_date or date.today()
    renewal.updated_at = now

    db.commit()
    db.refresh(renewal)

    return renewal


# ============================================================
# 8. UPCOMING RENEWALS
# ============================================================

@router.get(
    "/monitoring/upcoming",
    response_model=list[RenewalMonitoringResponse]
)
def get_upcoming_renewals(
    days: int = 90,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if days < 1 or days > 365:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="days must be between 1 and 365"
        )

    today = date.today()
    threshold = today + timedelta(days=days)

    # Renewal Monitoring is based on active contracts approaching
    # expiry, not on whether a Renewal workflow record already exists.
    contracts = db.query(Contract).filter(
        Contract.end_date >= today,
        Contract.end_date <= threshold,
        Contract.status == "Active"
    ).order_by(
        Contract.end_date.asc()
    ).all()

    renewals = []

    for contract in contracts:
        renewal = db.query(Renewal).filter(
            Renewal.contract_id == contract.id,
            Renewal.status.in_(["Upcoming", "In Progress"])
        ).order_by(
            Renewal.id.desc()
        ).first()

        if renewal is not None:
            renewals.append(renewal)
            continue

        # Build a monitoring-only response.
        renewals.append(
            RenewalMonitoringResponse(
                id=contract.id,
                contract_id=contract.id,
                renewal_date=None,
                previous_expiry_date=contract.end_date,
                new_expiry_date=None,
                status="Upcoming",
                assigned_to=contract.assigned_to,
                notes="Automatic renewal monitoring record",
                created_at=contract.updated_at or contract.created_at,
                updated_at=contract.updated_at or contract.created_at
            )
        )

    return renewals


# ============================================================
# 9. EXPIRED CONTRACTS / RENEWALS
# ============================================================

@router.get(
    "/monitoring/expired",
    response_model=list[RenewalMonitoringResponse]
)
def get_expired_renewals(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today = date.today()

    # Renewal Monitoring checks active contracts whose expiry date
    # has already passed, regardless of whether a Renewal workflow
    # record exists.
    contracts = db.query(Contract).filter(
        Contract.end_date < today,
        Contract.status == "Active"
    ).order_by(
        Contract.end_date.asc()
    ).all()

    renewals = []

    for contract in contracts:
        renewal = db.query(Renewal).filter(
            Renewal.contract_id == contract.id,
            Renewal.status.in_(["Upcoming", "In Progress", "Expired"])
        ).order_by(
            Renewal.id.desc()
        ).first()

        if renewal is not None:
            if renewal.status in {"Upcoming", "In Progress"}:
                renewal.status = "Expired"
                renewal.updated_at = datetime.now(
                    timezone.utc
                ).replace(tzinfo=None)

            renewals.append(renewal)
            continue

        monitoring_renewal = Renewal(
            id=0,
            contract_id=contract.id,
            renewal_date=None,
            previous_expiry_date=contract.end_date,
            new_expiry_date=None,
            status="Expired",
            assigned_to=contract.assigned_to,
            notes="Automatic renewal monitoring record",
            created_at=contract.updated_at or contract.created_at,
            updated_at=contract.updated_at or contract.created_at
        )

        renewals.append(monitoring_renewal)

    db.commit()

    return renewals


# Required Sprint 10 endpoint:
# GET /contracts/{contract_id}/renewals

from fastapi import APIRouter

contract_renewals_router = APIRouter(
    prefix="/contracts",
    tags=["Renewals"]
)


@contract_renewals_router.get(
    "/{contract_id}/renewals",
    response_model=list[RenewalResponse]
)
def get_contract_renewal_history(
    contract_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    get_contract_or_404(contract_id, db)

    return db.query(Renewal).filter(
        Renewal.contract_id == contract_id
    ).order_by(
        Renewal.id.asc()
    ).all()
