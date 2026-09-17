# app/routers/renewals.py

from datetime import date, timedelta

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
    RenewalResponse
)

# ---------------------------------------------------------
# IMPORTANT
# Change this import if your get_current_user is located
# somewhere else in your project.
# ---------------------------------------------------------
from app.core.security import get_current_user


router = APIRouter(
    prefix="/renewals",
    tags=["Renewals"]
)


# =========================================================
# ALLOWED STATUS VALUES
# =========================================================

ALLOWED_STATUSES = {
    "Upcoming",
    "In Progress",
    "Renewed",
    "Expired",
    "Cancelled"
}


# =========================================================
# VALID STATUS TRANSITIONS
# =========================================================

VALID_TRANSITIONS = {
    "Upcoming": {
        "In Progress",
        "Expired",
        "Cancelled"
    },

    "In Progress": {
        "Renewed",
        "Cancelled",
        "Expired"
    },

    "Renewed": set(),

    "Expired": set(),

    "Cancelled": set()
}


# =========================================================
# 1. CREATE RENEWAL
# POST /renewals
# =========================================================

@router.post(
    "",
    response_model=RenewalResponse,
    status_code=status.HTTP_201_CREATED
)
def create_renewal(
    data: RenewalCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Check contract
    contract = db.query(Contract).filter(
        Contract.id == data.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail=f"Contract {data.contract_id} not found"
        )

    # Check assigned user
    if data.assigned_to is not None:

        user = db.query(User).filter(
            User.id == data.assigned_to
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User {data.assigned_to} not found"
            )

    # Validate date
    if (
        data.new_expiry_date is not None
        and data.new_expiry_date < data.renewal_date
    ):
        raise HTTPException(
            status_code=400,
            detail="New expiry date cannot be earlier than renewal date"
        )

    # Create renewal
    renewal = Renewal(
        contract_id=data.contract_id,
        renewal_date=data.renewal_date,
        previous_expiry_date=data.previous_expiry_date,
        new_expiry_date=data.new_expiry_date,
        assigned_to=data.assigned_to,
        notes=data.notes,
        status="Upcoming"
    )

    db.add(renewal)
    db.commit()
    db.refresh(renewal)

    return renewal


# =========================================================
# 2. GET ALL RENEWALS
# GET /renewals
# =========================================================

@router.get(
    "",
    response_model=list[RenewalResponse]
)
def get_renewals(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    renewals = db.query(Renewal).all()

    return renewals


# =========================================================
# 3. GET RENEWAL BY ID
# GET /renewals/{renewal_id}
# =========================================================

@router.get(
    "/{renewal_id}",
    response_model=RenewalResponse
)
def get_renewal(
    renewal_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=404,
            detail=f"Renewal {renewal_id} not found"
        )

    return renewal


# =========================================================
# 4. GET RENEWALS FOR CONTRACT
# GET /renewals/contract/{contract_id}
# =========================================================

@router.get(
    "/contract/{contract_id}",
    response_model=list[RenewalResponse]
)
def get_contract_renewals(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail=f"Contract {contract_id} not found"
        )

    renewals = db.query(Renewal).filter(
        Renewal.contract_id == contract_id
    ).all()

    return renewals


# =========================================================
# 5. UPDATE RENEWAL
# PUT /renewals/{renewal_id}
# =========================================================

@router.put(
    "/{renewal_id}",
    response_model=RenewalResponse
)
def update_renewal(
    renewal_id: int,
    data: RenewalUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=404,
            detail=f"Renewal {renewal_id} not found"
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    # Check assigned user
    if "assigned_to" in update_data:

        if update_data["assigned_to"] is not None:

            user = db.query(User).filter(
                User.id == update_data["assigned_to"]
            ).first()

            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="Assigned user not found"
                )

    # Validate new expiry
    if "new_expiry_date" in update_data:

        new_expiry = update_data["new_expiry_date"]

        if (
            new_expiry is not None
            and new_expiry < renewal.renewal_date
        ):
            raise HTTPException(
                status_code=400,
                detail="New expiry date cannot be earlier than renewal date"
            )

    # Validate renewal date
    if "renewal_date" in update_data:

        renewal_date = update_data["renewal_date"]

        if (
            renewal.new_expiry_date is not None
            and renewal.new_expiry_date < renewal_date
        ):
            raise HTTPException(
                status_code=400,
                detail="Renewal date cannot be after new expiry date"
            )

    for key, value in update_data.items():
        setattr(renewal, key, value)

    db.commit()
    db.refresh(renewal)

    return renewal


# =========================================================
# 6. UPDATE RENEWAL STATUS
# PATCH /renewals/{renewal_id}/status
# =========================================================

@router.patch(
    "/{renewal_id}/status",
    response_model=RenewalResponse
)
def update_renewal_status(
    renewal_id: int,
    data: RenewalStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=404,
            detail=f"Renewal {renewal_id} not found"
        )

    new_status = data.status

    # Check status name
    if new_status not in ALLOWED_STATUSES:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid status '{new_status}'. "
                f"Allowed statuses: "
                f"{', '.join(ALLOWED_STATUSES)}"
            )
        )

    # Check transition
    allowed_next_statuses = VALID_TRANSITIONS.get(
        renewal.status,
        set()
    )

    if new_status not in allowed_next_statuses:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid status transition: "
                f"{renewal.status} -> {new_status}"
            )
        )

    renewal.status = new_status

    db.commit()
    db.refresh(renewal)

    return renewal


# =========================================================
# 7. COMPLETE / RENEW CONTRACT
# POST /renewals/{renewal_id}/renew
# =========================================================

@router.post(
    "/{renewal_id}/renew",
    response_model=RenewalResponse
)
def complete_renewal(
    renewal_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=404,
            detail=f"Renewal {renewal_id} not found"
        )

    # Renewal must be In Progress
    if renewal.status != "In Progress":

        raise HTTPException(
            status_code=400,
            detail=(
                "Renewal can only be completed "
                "when status is 'In Progress'"
            )
        )

    # New expiry date is required
    if renewal.new_expiry_date is None:

        raise HTTPException(
            status_code=400,
            detail="New expiry date is required to renew the contract"
        )

    # Update renewal
    renewal.status = "Renewed"

    # Update associated contract
    contract = db.query(Contract).filter(
        Contract.id == renewal.contract_id
    ).first()

    if contract:

        contract.end_date = renewal.new_expiry_date

        # Keep contract active after renewal
        contract.status = "Active"

    db.commit()
    db.refresh(renewal)

    return renewal


# =========================================================
# 8. UPCOMING RENEWALS
# GET /renewals/upcoming
# =========================================================

@router.get(
    "/upcoming",
    response_model=list[RenewalResponse]
)
def get_upcoming_renewals(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    today = date.today()

    threshold_date = today + timedelta(days=90)

    renewals = db.query(Renewal).filter(
        Renewal.previous_expiry_date >= today,
        Renewal.previous_expiry_date <= threshold_date,
        Renewal.status.in_([
            "Upcoming",
            "In Progress"
        ])
    ).all()

    return renewals


# =========================================================
# 9. EXPIRED RENEWALS
# GET /renewals/expired
# =========================================================

@router.get(
    "/expired",
    response_model=list[RenewalResponse]
)
def get_expired_renewals(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    today = date.today()

    renewals = db.query(Renewal).filter(
        Renewal.previous_expiry_date < today,
        Renewal.status.in_([
            "Upcoming",
            "In Progress"
        ])
    ).all()

    return renewals


# =========================================================
# 10. DELETE RENEWAL
# DELETE /renewals/{renewal_id}
# =========================================================

@router.delete(
    "/{renewal_id}"
)
def delete_renewal(
    renewal_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:

        raise HTTPException(
            status_code=404,
            detail=f"Renewal {renewal_id} not found"
        )

    db.delete(renewal)
    db.commit()

    return {
        "message": f"Renewal {renewal_id} deleted successfully"
    }