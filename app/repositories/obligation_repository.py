from typing import Optional

from sqlalchemy.orm import Session

from app.models.obligation import Obligation
from app.schemas.obligation import ObligationCreate


def create_obligation(db: Session, obligation: ObligationCreate) -> Obligation:
    db_obligation = Obligation(**obligation.model_dump())
    db.add(db_obligation)
    db.commit()
    db.refresh(db_obligation)
    return db_obligation


def get_obligation(db: Session, obligation_id: int) -> Optional[Obligation]:
    return db.query(Obligation).filter(Obligation.id == obligation_id).first()


def get_obligations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Obligation).offset(skip).limit(limit).all()


def get_obligations_by_contract(db: Session, contract_id: int):
    return db.query(Obligation).filter(Obligation.contract_id == contract_id).all()


def update_obligation_status(
    db: Session, obligation_id: int, status: str
) -> Optional[Obligation]:
    obligation = get_obligation(db, obligation_id)
    if not obligation:
        return None
    obligation.status = status
    db.commit()
    db.refresh(obligation)
    return obligation


def delete_obligation(db: Session, obligation_id: int) -> bool:
    obligation = get_obligation(db, obligation_id)
    if not obligation:
        return False
    db.delete(obligation)
    db.commit()
    return True
