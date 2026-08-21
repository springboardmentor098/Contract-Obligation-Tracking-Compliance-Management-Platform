from datetime import datetime

from sqlalchemy.orm import Session

from app.models.contracts import Contract
from app.schemas.contract import ContractCreate, ContractUpdate


VALID_STATUSES = [
    "Draft",
    "Under Review",
    "Approved",
    "Active",
    "Expired",
    "Terminated",
]


def create_contract(
    db: Session,
    contract_data: ContractCreate,
    user_id: int
):
    contract = Contract(
        created_by=user_id,
        title=contract_data.title,
        contract_number=contract_data.contract_number,
        category=contract_data.category,
        description=contract_data.description,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        status="Draft"
    )

    db.add(contract)
    db.commit()
    db.refresh(contract)

    return contract


def get_all_contracts(db: Session):
    return db.query(Contract).all()


def get_contract_by_id(db: Session, contract_id: int):
    return db.query(Contract).filter(
        Contract.id == contract_id
    ).first()


def update_contract(
    db: Session,
    contract_id: int,
    contract_data: ContractUpdate
):
    contract = get_contract_by_id(db, contract_id)

    if not contract:
        return None

    update_data = contract_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(contract, field, value)

    db.commit()
    db.refresh(contract)

    return contract


def update_contract_status(
    db: Session,
    contract_id: int,
    new_status: str
):
    contract = get_contract_by_id(db, contract_id)

    if not contract:
        return None, "Contract not found"

    if new_status not in VALID_STATUSES:
        return None, "Invalid contract status"

    current_status = contract.status

    valid_transitions = {
        "Draft": ["Under Review", "Terminated"],
        "Under Review": ["Approved", "Draft", "Terminated"],
        "Approved": ["Active", "Terminated"],
        "Active": ["Expired", "Terminated"],
        "Expired": [],
        "Terminated": [],
    }

    if new_status not in valid_transitions.get(current_status, []):
        return None, (
            f"Invalid status transition: "
            f"{current_status} -> {new_status}"
        )

    contract.status = new_status

    if new_status == "Under Review":
        contract.reviewed_at = datetime.utcnow()

    if new_status == "Approved":
        contract.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract, None


def submit_for_review(
    db: Session,
    contract_id: int
):
    contract = get_contract_by_id(db, contract_id)

    if not contract:
        return None, "Contract not found"

    if contract.status != "Draft":
        return None, (
            f"Invalid status transition: "
            f"{contract.status} -> Under Review"
        )

    contract.status = "Under Review"
    contract.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract, None


def approve_contract(
    db: Session,
    contract_id: int
):
    contract = get_contract_by_id(db, contract_id)

    if not contract:
        return None, "Contract not found"

    if contract.status != "Under Review":
        return None, (
            f"Invalid status transition: "
            f"{contract.status} -> Approved"
        )

    contract.status = "Approved"
    contract.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    return contract, None


def activate_contract(
    db: Session,
    contract_id: int
):
    contract = get_contract_by_id(db, contract_id)

    if not contract:
        return None, "Contract not found"

    if contract.status != "Approved":
        return None, (
            f"Invalid status transition: "
            f"{contract.status} -> Active"
        )

    contract.status = "Active"

    db.commit()
    db.refresh(contract)

    return contract, None
