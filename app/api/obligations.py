from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.obligation import ObligationCreate, ObligationResponse
from app.services.obligation_service import ObligationService

router = APIRouter(prefix="/obligations", tags=["Obligations"])


@router.post("/", response_model=ObligationResponse)
def create_obligation(obligation: ObligationCreate, db: Session = Depends(get_db)):
    service = ObligationService(db)
    return service.create_obligation(obligation)


@router.get("/{obligation_id}", response_model=ObligationResponse)
def read_obligation(obligation_id: int, db: Session = Depends(get_db)):
    service = ObligationService(db)
    obligation = service.get_obligation(obligation_id)
    if not obligation:
        raise HTTPException(status_code=404, detail="Obligation not found")
    return obligation


@router.get("/", response_model=list[ObligationResponse])
def list_obligations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = ObligationService(db)
    return service.list_obligations(skip, limit)


@router.get("/contract/{contract_id}", response_model=list[ObligationResponse])
def list_by_contract(contract_id: int, db: Session = Depends(get_db)):
    service = ObligationService(db)
    return service.list_by_contract(contract_id)


@router.patch("/{obligation_id}/status", response_model=ObligationResponse)
def update_status(obligation_id: int, status: str, db: Session = Depends(get_db)):
    service = ObligationService(db)
    obligation = service.update_status(obligation_id, status)
    if not obligation:
        raise HTTPException(status_code=404, detail="Obligation not found")
    return obligation


@router.delete("/{obligation_id}")
def delete_obligation(obligation_id: int, db: Session = Depends(get_db)):
    service = ObligationService(db)
    if not service.delete_obligation(obligation_id):
        raise HTTPException(status_code=404, detail="Obligation not found")
    return {"detail": "Obligation deleted"}
