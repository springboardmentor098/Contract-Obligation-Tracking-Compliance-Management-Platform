from typing import Optional

from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.schemas.contract import ContractCreate


def create_contract(db: Session, contract: ContractCreate) -> Contract:
    db_contract = Contract(**contract.model_dump())
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract


def get_contract(db: Session, contract_id: int) -> Optional[Contract]:
    return db.query(Contract).filter(Contract.id == contract_id).first()


def get_contracts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Contract).offset(skip).limit(limit).all()


def delete_contract(db: Session, contract_id: int) -> bool:
    contract = get_contract(db, contract_id)
    if not contract:
        return False
    db.delete(contract)
    db.commit()
    return True
