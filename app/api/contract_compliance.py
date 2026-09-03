from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Contract
from app.core.deps import get_current_user
from app.services.compliance_service import evaluate_contract
from app.schemas.compliance import ComplianceResponse
router=APIRouter(prefix="/contracts",tags=["Compliance"])
@router.get("/{contract_id}/compliance",response_model=ComplianceResponse)
def contract_compliance(contract_id:int,user=Depends(get_current_user),db:Session=Depends(get_db)):
    c=db.get(Contract,contract_id)
    if not c: raise HTTPException(404,"Contract not found")
    return evaluate_contract(db,c,persist=True)
