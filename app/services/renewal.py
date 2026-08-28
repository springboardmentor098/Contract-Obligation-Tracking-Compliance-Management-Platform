from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.renewal import Renewal
from app.models.contracts import Contract
from app.models.user import User
from app.schemas.renewal import RenewalCreate, RenewalUpdate


def create_renewal(db: Session, data: RenewalCreate):

    contract = db.query(Contract).filter(
        Contract.id == data.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found"
        )

    user = db.query(User).filter(
        User.id == data.assigned_to
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Assigned user not found"
        )

    if data.new_expiry_date < data.renewal_date:
        raise HTTPException(
            status_code=400,
            detail="New expiry date cannot be earlier than renewal date"
        )

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


def get_all_renewals(db: Session):

    renewals = db.query(Renewal).all()

    return renewals


def get_renewal_by_id(db: Session, renewal_id: int):

    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=404,
            detail="Renewal not found"
        )

    return renewal


def get_contract_renewals(db: Session, contract_id: int):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found"
        )

    return db.query(Renewal).filter(
        Renewal.contract_id == contract_id
    ).all()


def update_renewal(
    db: Session,
    renewal_id: int,
    data: RenewalUpdate
):

    renewal = get_renewal_by_id(db, renewal_id)

    if data.renewal_date is not None:
        renewal.renewal_date = data.renewal_date

    if data.new_expiry_date is not None:
        renewal.new_expiry_date = data.new_expiry_date

    if data.assigned_to is not None:

        user = db.query(User).filter(
            User.id == data.assigned_to
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Assigned user not found"
            )

        renewal.assigned_to = data.assigned_to

    if data.notes is not None:
        renewal.notes = data.notes

    if renewal.new_expiry_date < renewal.renewal_date:
        raise HTTPException(
            status_code=400,
            detail="New expiry date cannot be earlier than renewal date"
        )

    db.commit()
    db.refresh(renewal)

    return renewal


def update_renewal_status(
    db: Session,
    renewal_id: int,
    status: str
):

    renewal = get_renewal_by_id(db, renewal_id)

    allowed_statuses = [
        "Upcoming",
        "In Progress",
        "Renewed",
        "Expired",
        "Cancelled"
    ]

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid renewal status"
        )

    current = renewal.status

    valid_transitions = {
        "Upcoming": ["In Progress", "Expired", "Cancelled"],
        "In Progress": ["Renewed", "Cancelled"],
        "Renewed": [],
        "Expired": [],
        "Cancelled": []
    }

    if status not in valid_transitions.get(current, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition: {current} -> {status}"
        )

    renewal.status = status

    db.commit()
    db.refresh(renewal)

    return renewal


def complete_renewal(db: Session, renewal_id: int):

    renewal = get_renewal_by_id(db, renewal_id)

    if renewal.status != "In Progress":
        raise HTTPException(
            status_code=400,
            detail="Renewal must be In Progress before it can be completed"
        )

    renewal.status = "Renewed"

    contract = db.query(Contract).filter(
        Contract.id == renewal.contract_id
    ).first()

    if contract:
        contract.end_date = renewal.new_expiry_date
        contract.status = "Active"

    db.commit()
    db.refresh(renewal)

    return renewal


def get_upcoming_renewals(db: Session):

    today = date.today()

    renewals = db.query(Renewal).filter(
        Renewal.status == "Upcoming"
    ).all()

    result = []

    for renewal in renewals:

        days_remaining = (
            renewal.previous_expiry_date - today
        ).days

        if 0 <= days_remaining <= 90:
            result.append(renewal)

    return result


def get_expired_renewals(db: Session):

    today = date.today()

    renewals = db.query(Renewal).filter(
        Renewal.previous_expiry_date < today,
        Renewal.status == "Upcoming"
    ).all()

    return renewals
