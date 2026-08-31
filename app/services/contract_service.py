from sqlalchemy.orm import Session

from app.repositories import contract_repository
from app.schemas.contract import ContractCreate


class ContractService:
    def __init__(self, db: Session):
        self.db = db

    def create_contract(self, contract: ContractCreate):
        return contract_repository.create_contract(self.db, contract)

    def get_contract(self, contract_id: int):
        return contract_repository.get_contract(self.db, contract_id)

    def list_contracts(self, skip: int = 0, limit: int = 100):
        return contract_repository.get_contracts(self.db, skip, limit)

    def delete_contract(self, contract_id: int):
        return contract_repository.delete_contract(self.db, contract_id)
