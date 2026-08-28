from datetime import date, datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.contract import Contract
from app.models.renewal import Renewal
from app.models.user import User
from app.schemas.renewal import (
    ExpiredContractResponse,
    RenewalComplete,
    RenewalCreate,
    RenewalResponse,
    RenewalStatusUpdate,
    RenewalUpdate,
    UpcomingRenewalResponse,
    VALID_RENEWAL_STATUSES,
    VALID_STATUS_TRANSITIONS,
)

router = APIRouter(
    tags=["Renewals"]
)


@router.post(
    "/renewals",
    response_model=RenewalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Renewal Record",
    description="Creates a new renewal record for an existing contract."
)
def create_renewal(
    renewal_in: RenewalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new renewal record."""
    # 1. Verify contract exists
    contract = db.query(Contract).filter(Contract.id == renewal_in.contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {renewal_in.contract_id} not found."
        )

    # 2. Verify assigned user exists if provided
    if renewal_in.assigned_to is not None:
        assigned_user = db.query(User).filter(
            (User.user_id == renewal_in.assigned_to) | (User.id == renewal_in.assigned_to)
        ).first()
        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assigned user with ID {renewal_in.assigned_to} not found."
            )

    # 3. Date range validation
    prev_expiry = renewal_in.previous_expiry_date or contract.end_date
    new_expiry = renewal_in.new_expiry_date
    ren_date = renewal_in.renewal_date

    if new_expiry and prev_expiry and new_expiry < prev_expiry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New expiry date cannot be earlier than previous expiry date."
        )

    if new_expiry and ren_date and new_expiry < ren_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New expiry date cannot be earlier than renewal date."
        )

    init_status = renewal_in.status if renewal_in.status in VALID_RENEWAL_STATUSES else "Upcoming"

    new_renewal = Renewal(
        contract_id=renewal_in.contract_id,
        renewal_date=renewal_in.renewal_date,
        previous_expiry_date=prev_expiry,
        new_expiry_date=new_expiry,
        status=init_status,
        assigned_to=renewal_in.assigned_to,
        notes=renewal_in.notes.strip() if renewal_in.notes else None
    )

    db.add(new_renewal)
    db.commit()
    db.refresh(new_renewal)

    return new_renewal


@router.get(
    "/renewals",
    response_model=List[RenewalResponse],
    status_code=status.HTTP_200_OK,
    summary="Get All Renewals",
    description="Retrieves all renewal records with optional filtering by status or contract_id."
)
def get_all_renewals(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by renewal status"),
    contract_id: Optional[int] = Query(None, description="Filter by contract ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all renewal records."""
    query = db.query(Renewal)
    if status_filter:
        query = query.filter(Renewal.status == status_filter)
    if contract_id:
        query = query.filter(Renewal.contract_id == contract_id)
    return query.all()


@router.get(
    "/renewals/upcoming",
    response_model=List[UpcomingRenewalResponse],
    status_code=status.HTTP_200_OK,
    summary="Upcoming Renewal Detection",
    description="Identifies contracts approaching their expiry date within a given number of days."
)
def get_upcoming_renewals(
    days: int = Query(30, ge=1, le=365, description="Number of days threshold to check upcoming expiry"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Detect contracts approaching expiry within specified days."""
    today = date.today()
    target_date = today + timedelta(days=days)

    contracts = db.query(Contract).filter(
        Contract.end_date.isnot(None),
        Contract.end_date >= today,
        Contract.end_date <= target_date
    ).all()

    upcoming_list = []
    for c in contracts:
        days_rem = (c.end_date - today).days
        upcoming_list.append(UpcomingRenewalResponse(
            contract_id=c.id,
            title=c.title,
            contract_number=c.contract_number,
            end_date=c.end_date,
            days_remaining=days_rem,
            status="Upcoming"
        ))

    return upcoming_list


@router.get(
    "/renewals/expired",
    response_model=List[ExpiredContractResponse],
    status_code=status.HTTP_200_OK,
    summary="Expired Contract Detection",
    description="Identifies contracts whose expiry date has passed and are not renewed."
)
def get_expired_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Detect contracts whose end date has passed."""
    today = date.today()

    contracts = db.query(Contract).filter(
        Contract.end_date.isnot(None),
        Contract.end_date < today
    ).all()

    expired_list = []
    for c in contracts:
        days_exp = (today - c.end_date).days
        expired_list.append(ExpiredContractResponse(
            contract_id=c.id,
            title=c.title,
            contract_number=c.contract_number,
            end_date=c.end_date,
            days_expired=days_exp,
            status="Expired"
        ))

    return expired_list


@router.get(
    "/renewals/{renewal_id}",
    response_model=RenewalResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Renewal by ID",
    description="Retrieves a specific renewal record by its ID."
)
def get_renewal_by_id(
    renewal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get renewal record by ID."""
    renewal = db.query(Renewal).filter((Renewal.id == renewal_id) | (Renewal.renewal_id == renewal_id)).first()
    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Renewal record with ID {renewal_id} not found."
        )
    return renewal


@router.get(
    "/contracts/{contract_id}/renewals",
    response_model=List[RenewalResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Renewals for a Contract",
    description="Retrieves all renewal records associated with a specific contract."
)
def get_contract_renewals(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all renewal history for a contract."""
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found."
        )

    renewals = db.query(Renewal).filter(Renewal.contract_id == contract_id).all()
    return renewals


@router.put(
    "/renewals/{renewal_id}",
    response_model=RenewalResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Renewal Record",
    description="Updates editable details of an existing renewal record."
)
def update_renewal(
    renewal_id: int,
    renewal_in: RenewalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update renewal details."""
    renewal = db.query(Renewal).filter((Renewal.id == renewal_id) | (Renewal.renewal_id == renewal_id)).first()
    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Renewal record with ID {renewal_id} not found."
        )

    if renewal_in.assigned_to is not None:
        assigned_user = db.query(User).filter(
            (User.user_id == renewal_in.assigned_to) | (User.id == renewal_in.assigned_to)
        ).first()
        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assigned user with ID {renewal_in.assigned_to} not found."
            )
        renewal.assigned_to = renewal_in.assigned_to

    if renewal_in.renewal_date is not None:
        renewal.renewal_date = renewal_in.renewal_date

    if renewal_in.previous_expiry_date is not None:
        renewal.previous_expiry_date = renewal_in.previous_expiry_date

    if renewal_in.new_expiry_date is not None:
        # Validate date range
        prev = renewal_in.previous_expiry_date or renewal.previous_expiry_date
        ren = renewal_in.renewal_date or renewal.renewal_date
        if prev and renewal_in.new_expiry_date < prev:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New expiry date cannot be earlier than previous expiry date."
            )
        if ren and renewal_in.new_expiry_date < ren:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New expiry date cannot be earlier than renewal date."
            )
        renewal.new_expiry_date = renewal_in.new_expiry_date

    if renewal_in.notes is not None:
        renewal.notes = renewal_in.notes.strip() if renewal_in.notes else None

    db.commit()
    db.refresh(renewal)
    return renewal


@router.patch(
    "/renewals/{renewal_id}/status",
    response_model=RenewalResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Renewal Status",
    description="Updates the renewal status enforcing valid status lifecycle transitions."
)
def update_renewal_status(
    renewal_id: int,
    status_in: RenewalStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update renewal status with lifecycle validation."""
    renewal = db.query(Renewal).filter((Renewal.id == renewal_id) | (Renewal.renewal_id == renewal_id)).first()
    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Renewal record with ID {renewal_id} not found."
        )

    new_status = status_in.status.strip()
    if new_status not in VALID_RENEWAL_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid renewal status '{new_status}'. Allowed statuses: {VALID_RENEWAL_STATUSES}"
        )

    current_status = renewal.status
    allowed_transitions = VALID_STATUS_TRANSITIONS.get(current_status, [])

    if new_status not in allowed_transitions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from '{current_status}' to '{new_status}'. Allowed transitions: {allowed_transitions}"
        )

    renewal.status = new_status
    db.commit()
    db.refresh(renewal)
    return renewal


@router.post(
    "/renewals/{renewal_id}/renew",
    response_model=RenewalResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete Renewal",
    description="Completes the renewal process: sets status to Renewed and updates the contract's expiry date."
)
def complete_renewal(
    renewal_id: int,
    complete_in: Optional[RenewalComplete] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete a renewal event, transition status to Renewed, and update the associated contract."""
    renewal = db.query(Renewal).filter((Renewal.id == renewal_id) | (Renewal.renewal_id == renewal_id)).first()
    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Renewal record with ID {renewal_id} not found."
        )

    target_new_expiry = None
    if complete_in and complete_in.new_expiry_date:
        target_new_expiry = complete_in.new_expiry_date
    elif renewal.new_expiry_date:
        target_new_expiry = renewal.new_expiry_date

    if not target_new_expiry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A valid new_expiry_date must be recorded to complete the renewal."
        )

    if complete_in and complete_in.notes:
        renewal.notes = complete_in.notes.strip()

    renewal.new_expiry_date = target_new_expiry
    renewal.status = "Renewed"

    # Update associated contract's end_date
    contract = db.query(Contract).filter(Contract.id == renewal.contract_id).first()
    if contract:
        contract.end_date = target_new_expiry

    db.commit()
    db.refresh(renewal)
    return renewal
