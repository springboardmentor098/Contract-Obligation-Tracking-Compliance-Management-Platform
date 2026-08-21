from datetime import date

from sqlalchemy.orm import Session

from app.models.obligations import Obligation
from app.schemas.obligation import (
    ObligationCreate,
    ObligationUpdate,
)


VALID_STATUSES = [
    "Pending",
    "In Progress",
    "Completed",
    "Delayed",
    "Overdue",
]


def create_obligation(
    db: Session,
    obligation_data: ObligationCreate
):
    obligation = Obligation(
        contract_id=obligation_data.contract_id,
        title=obligation_data.title,
        description=obligation_data.description,
        obligation_type=obligation_data.obligation_type,
        due_date=obligation_data.due_date,
        assigned_to=obligation_data.assigned_to,
        status="Pending",
    )

    db.add(obligation)
    db.commit()
    db.refresh(obligation)

    return obligation


def get_all_obligations(db: Session):
    obligations = db.query(Obligation).all()
    print("========== OBLIGATIONS ==========")

    for o in obligations:
        print(
            o.id,
            o.title,
            o.obligation_type,
            o.assigned_to,
            o.created_at,
            o.updated_at
        )

    print("=================================")

    # Identify overdue obligations automatically
    today = date.today()

    for obligation in obligations:
        if (
            obligation.status in ["Pending", "In Progress"]
            and obligation.due_date < today
        ):
            obligation.status = "Overdue"

    db.commit()

    return obligations


def get_obligation_by_id(
    db: Session,
    obligation_id: int
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if obligation and (
        obligation.status in ["Pending", "In Progress"]
        and obligation.due_date < date.today()
    ):
        obligation.status = "Overdue"
        db.commit()
        db.refresh(obligation)

    return obligation


def get_contract_obligations(
    db: Session,
    contract_id: int
):
    return db.query(Obligation).filter(
        Obligation.contract_id == contract_id
    ).all()


def update_obligation(
    db: Session,
    obligation_id: int,
    obligation_data: ObligationUpdate
):
    obligation = get_obligation_by_id(db, obligation_id)

    if not obligation:
        return None

    update_data = obligation_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(obligation, field, value)

    db.commit()
    db.refresh(obligation)

    return obligation


def update_obligation_status(
    db: Session,
    obligation_id: int,
    new_status: str
):
    obligation = get_obligation_by_id(db, obligation_id)

    if not obligation:
        return None, "Obligation not found"

    if new_status not in VALID_STATUSES:
        return None, "Invalid obligation status"

    valid_transitions = {
        "Pending": ["In Progress", "Delayed"],
        "In Progress": ["Completed", "Delayed"],
        "Delayed": ["In Progress", "Completed"],
        "Completed": [],
        "Overdue": ["In Progress", "Completed"],
    }

    if new_status not in valid_transitions.get(
        obligation.status,
        []
    ):
        return None, (
            f"Invalid status transition: "
            f"{obligation.status} -> {new_status}"
        )

    obligation.status = new_status

    db.commit()
    db.refresh(obligation)

    return obligation, None


def complete_obligation(
    db: Session,
    obligation_id: int
):
    obligation = get_obligation_by_id(db, obligation_id)

    if not obligation:
        return None, "Obligation not found"

    if obligation.status not in [
        "In Progress",
        "Delayed",
        "Overdue"
    ]:
        return None, (
            f"Cannot complete obligation from "
            f"{obligation.status} status"
        )

    obligation.status = "Completed"
    obligation.completion_date = date.today()

    db.commit()
    db.refresh(obligation)

    return obligation, None