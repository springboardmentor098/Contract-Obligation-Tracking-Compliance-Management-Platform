from sqlalchemy.orm import Session

from app.repositories import obligation_repository
from app.schemas.obligation import ObligationCreate


class ObligationService:
    def __init__(self, db: Session):
        self.db = db

    def create_obligation(self, obligation: ObligationCreate):
        return obligation_repository.create_obligation(self.db, obligation)

    def get_obligation(self, obligation_id: int):
        return obligation_repository.get_obligation(self.db, obligation_id)

    def list_obligations(self, skip: int = 0, limit: int = 100):
        return obligation_repository.get_obligations(self.db, skip, limit)

    def list_by_contract(self, contract_id: int):
        return obligation_repository.get_obligations_by_contract(self.db, contract_id)

    def update_status(self, obligation_id: int, status: str):
        return obligation_repository.update_obligation_status(
            self.db, obligation_id, status
        )

    def delete_obligation(self, obligation_id: int):
        return obligation_repository.delete_obligation(self.db, obligation_id)
