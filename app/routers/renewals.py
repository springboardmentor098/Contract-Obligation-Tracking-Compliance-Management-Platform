from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.contract import Contract
from app.models.renewal import Renewal
from app.models.user import User
from app.schemas.renewal import (
    RenewalCreate,
    RenewalResponse,
    RenewalStatusUpdate,
    RenewalUpdate
)


router = APIRouter(
    tags=["Renewals"]
)


# =========================
# CREATE RENEWAL
# =========================

@router.post(
    "/renewals",
    response_model=RenewalResponse,
    status_code=status.HTTP_201_CREATED
)
def create_renewal(
    renewal_data: RenewalCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    contract = db.query(Contract).filter(
        Contract.id == renewal_data.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    assigned_user = db.query(User).filter(
        User.id == renewal_data.assigned_to
    ).first()

    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )

    if renewal_data.new_expiry_date is not None:
        if renewal_data.new_expiry_date < renewal_data.renewal_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New expiry date cannot be earlier than renewal date"
            )

    renewal = Renewal(
        contract_id=renewal_data.contract_id,
        renewal_date=renewal_data.renewal_date,
        previous_expiry_date=renewal_data.previous_expiry_date,
        new_expiry_date=renewal_data.new_expiry_date,
        status="Upcoming",
        assigned_to=renewal_data.assigned_to,
        notes=renewal_data.notes
    )

    db.add(renewal)
    db.commit()
    db.refresh(renewal)

    return renewal


# =========================
# GET ALL RENEWALS
# =========================

@router.get(
    "/renewals",
    response_model=list[RenewalResponse],
    status_code=status.HTTP_200_OK
)
def get_renewals(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return db.query(Renewal).all()


# =========================
# GET RENEWAL BY ID
# =========================

@router.get(
    "/renewals/{renewal_id}",
    response_model=RenewalResponse,
    status_code=status.HTTP_200_OK
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


# =========================
# GET RENEWALS FOR CONTRACT
# =========================

@router.get(
    "/contracts/{contract_id}/renewals",
    response_model=list[RenewalResponse],
    status_code=status.HTTP_200_OK
)
def get_contract_renewals(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return db.query(Renewal).filter(
        Renewal.contract_id == contract_id
    ).all()


# =========================
# UPDATE RENEWAL
# =========================

@router.put(
    "/renewals/{renewal_id}",
    response_model=RenewalResponse,
    status_code=status.HTTP_200_OK
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

    if renewal.assigned_to != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this renewal"
        )

    if renewal_data.assigned_to is not None:
        assigned_user = db.query(User).filter(
            User.id == renewal_data.assigned_to
        ).first()

        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found"
            )

    if renewal_data.new_expiry_date is not None:
        renewal_date = (
            renewal_data.renewal_date
            if renewal_data.renewal_date is not None
            else renewal.renewal_date
        )

        if renewal_data.new_expiry_date < renewal_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New expiry date cannot be earlier than renewal date"
            )

    update_data = renewal_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(renewal, field, value)

    db.commit()
    db.refresh(renewal)

    return renewal


# =========================
# UPDATE RENEWAL STATUS
# =========================

@router.patch(
    "/renewals/{renewal_id}/status",
    response_model=RenewalResponse,
    status_code=status.HTTP_200_OK
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

    if renewal.assigned_to != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this renewal"
        )

    current_status = renewal.status
    new_status = status_data.status

    valid_transitions = {
        "Upcoming": ["In Progress", "Expired", "Cancelled"],
        "In Progress": ["Renewed", "Cancelled"],
        "Renewed": [],
        "Expired": [],
        "Cancelled": []
    }

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


# =========================
# COMPLETE / RENEW
# =========================

@router.post(
    "/renewals/{renewal_id}/renew",
    response_model=RenewalResponse,
    status_code=status.HTTP_200_OK
)
def renew_contract(
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

    if renewal.assigned_to != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to renew this contract"
        )

    if renewal.status != "In Progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only In Progress renewals can be completed"
        )

    if renewal.new_expiry_date is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New expiry date is required to renew the contract"
        )

    contract = db.query(Contract).filter(
        Contract.id == renewal.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    renewal.status = "Renewed"

    contract.end_date = renewal.new_expiry_date

    db.commit()
    db.refresh(renewal)

    return renewal