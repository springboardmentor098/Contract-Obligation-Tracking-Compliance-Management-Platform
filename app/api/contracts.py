from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.contract import ContractCreate, ContractResponse
from app.services.contract_service import ContractService

router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.post("/", response_model=ContractResponse)
def create_contract(contract: ContractCreate, db: Session = Depends(get_db)):
    service = ContractService(db)
    return service.create_contract(contract)


@router.get("/{contract_id}", response_model=ContractResponse)
def read_contract(contract_id: int, db: Session = Depends(get_db)):
    service = ContractService(db)
    contract = service.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.get("/", response_model=list[ContractResponse])
def list_contracts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = ContractService(db)
    return service.list_contracts(skip, limit)


@router.delete("/{contract_id}")
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    service = ContractService(db)
    if not service.delete_contract(contract_id):
        raise HTTPException(status_code=404, detail="Contract not found")
    return {"detail": "Contract deleted"}
