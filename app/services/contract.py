from sqlalchemy.orm import Session

from app.models.contracts import Contract
from app.schemas.contract import ContractCreate


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