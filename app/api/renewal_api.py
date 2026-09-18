from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.renewal import Renewal
from app.models.contract import Contract
from app.models.user import User
from app.schemas.renewal_schema import (
    RenewalCreate,
    RenewalUpdate,
    RenewalStatusUpdate,
    RenewalResponse
)
from app.core.auth import get_current_user
from app.core.role_checker import require_non_viewer
from app.services.activity_service import log_activity


router = APIRouter(
    prefix="/renewals",
    tags=["Renewals"],
    dependencies=[Depends(require_non_viewer)],
)


# ---------------- CREATE RENEWAL ----------------

@router.post(
    "",
    response_model=RenewalResponse,
    status_code=status.HTTP_201_CREATED
)
@router.post(
    "/",
    response_model=RenewalResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False
)
def create_renewal(
    renewal_data: RenewalCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(
        Contract.id == renewal_data.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found"
        )

    user = db.query(User).filter(
        User.id == renewal_data.assigned_to
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Assigned user not found"
        )

    if renewal_data.new_expiry_date <= renewal_data.renewal_date:
        raise HTTPException(
            status_code=400,
            detail="New expiry date must be after renewal date"
        )

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

    # Automatically record CREATE_RENEWAL activity log
    log_activity(
        db=db,
        action="CREATE_RENEWAL",
        entity_type="Renewal",
        entity_id=renewal.id,
        contract_id=renewal.contract_id,
        description=f"Scheduled renewal for contract '{contract.title}' on {renewal.renewal_date}",
        user=current_user,
        request=request,
    )

    return renewal


# ---------------- GET ALL RENEWALS ----------------

@router.get(
    "",
    response_model=list[RenewalResponse]
)
@router.get(
    "/",
    response_model=list[RenewalResponse],
    include_in_schema=False
)
def get_renewals(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Renewal).all()


# ---------------- GET RENEWAL BY ID ----------------

@router.get(
    "/{renewal_id}",
    response_model=RenewalResponse
)
def get_renewal(
    renewal_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=404,
            detail="Renewal not found"
        )

    return renewal


# ---------------- GET RENEWALS FOR A CONTRACT ----------------

@router.get(
    "/contract/{contract_id}",
    response_model=list[RenewalResponse]
)
def get_contract_renewals(
    contract_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found"
        )

    renewals = db.query(Renewal).filter(
        Renewal.contract_id == contract_id
    ).all()

    return renewals


# ---------------- UPDATE RENEWAL ----------------

@router.put(
    "/{renewal_id}",
    response_model=RenewalResponse
)
def update_renewal(
    renewal_id: int,
    renewal_data: RenewalUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=404,
            detail="Renewal not found"
        )

    update_data = renewal_data.model_dump(exclude_unset=True)

    if "assigned_to" in update_data:
        user = db.query(User).filter(
            User.id == update_data["assigned_to"]
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Assigned user not found"
            )

    if (
        "new_expiry_date" in update_data
        and "renewal_date" in update_data
        and update_data["new_expiry_date"] <= update_data["renewal_date"]
    ):
        raise HTTPException(
            status_code=400,
            detail="New expiry date must be after renewal date"
        )

    for key, value in update_data.items():
        setattr(renewal, key, value)

    db.commit()
    db.refresh(renewal)

    log_activity(
        db=db,
        action="UPDATE_RENEWAL",
        entity_type="Renewal",
        entity_id=renewal.id,
        contract_id=renewal.contract_id,
        description=f"Updated renewal #{renewal.id}",
        user=current_user,
        request=request,
    )

    return renewal


# ---------------- UPDATE RENEWAL STATUS ----------------

@router.patch(
    "/{renewal_id}/status",
    response_model=RenewalResponse
)
def update_renewal_status(
    renewal_id: int,
    status_data: RenewalStatusUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=404,
            detail="Renewal not found"
        )

    workflow = {
        "Upcoming": ["In Progress", "Cancelled", "Expired"],
        "In Progress": ["Renewed", "Cancelled"],
        "Renewed": [],
        "Expired": [],
        "Cancelled": []
    }

    current = renewal.status
    new = status_data.status

    if new not in workflow.get(current, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition from '{current}' to '{new}'"
        )

    renewal.status = new

    db.commit()
    db.refresh(renewal)

    log_activity(
        db=db,
        action="UPDATE_RENEWAL_STATUS",
        entity_type="Renewal",
        entity_id=renewal.id,
        contract_id=renewal.contract_id,
        description=f"Updated renewal #{renewal.id} status to {new}",
        user=current_user,
        request=request,
    )

    return renewal


# ---------------- COMPLETE RENEWAL ----------------

@router.post(
    "/{renewal_id}/renew",
    response_model=RenewalResponse
)
def complete_renewal(
    renewal_id: int,
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=404,
            detail="Renewal not found"
        )

    if renewal.status != "In Progress":
        raise HTTPException(
            status_code=400,
            detail="Renewal must be In Progress before completion"
        )

    renewal.status = "Renewed"

    contract = db.query(Contract).filter(
        Contract.id == renewal.contract_id
    ).first()

    if contract:
        contract.end_date = renewal.new_expiry_date

    db.commit()
    db.refresh(renewal)

    log_activity(
        db=db,
        action="COMPLETE_RENEWAL",
        entity_type="Renewal",
        entity_id=renewal.id,
        contract_id=renewal.contract_id,
        description=f"Executed renewal for contract '{contract.title if contract else ''}' to {renewal.new_expiry_date}",
        user=current_user,
        request=request,
    )

    return renewal