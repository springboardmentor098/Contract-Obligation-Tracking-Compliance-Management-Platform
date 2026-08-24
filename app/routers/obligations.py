from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime

from app.database.database import get_db
from app.models.all_models import Obligation, Contract, User, ObligationStatus
from app.schemas.obligation import (
    ObligationCreate,
    ObligationResponse,
    ObligationUpdate,
    ObligationStatusUpdate
)
from app.core.security import get_current_user

# 🛡️ RoleChecker to enforce permissions
class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    def __call__(self, current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient Permission")
        return current_user

require_admin = RoleChecker(["Administrator", "Manager"]) 

# 🚀 Create the router (No prefix here so we can support both /obligations and /contracts/{id}/obligations)
router = APIRouter(tags=["Obligations"])

# ==========================================
# ⚙️ HELPER: OVERDUE DETECTION LOGIC
# ==========================================
def update_overdue_obligations(db: Session):
    """Automatically marks pending/in-progress obligations as overdue if the deadline passed."""
    today = date.today()
    overdue_obligations = db.query(Obligation).filter(
        Obligation.status.in_([ObligationStatus.PENDING, ObligationStatus.IN_PROGRESS]),
        Obligation.due_date < today
    ).all()
    
    for obs in overdue_obligations:
        obs.status = ObligationStatus.OVERDUE
    
    if overdue_obligations:
        db.commit()


# ==========================================
# 📝 OBLIGATION APIs
# ==========================================

# 1. Create Obligation
@router.post("/obligations", response_model=ObligationResponse, status_code=status.HTTP_201_CREATED)
def create_obligation(
    obs_data: ObligationCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    # Verify Contract exists
    contract = db.query(Contract).filter(Contract.id == obs_data.contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract Not Found")
    
    # Verify User exists
    assigned_user = db.query(User).filter(User.id == obs_data.assigned_to).first()
    if not assigned_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Assigned User")
    
    new_obs = Obligation(
        contract_id=obs_data.contract_id,
        title=obs_data.title,
        description=obs_data.description,
        obligation_type=obs_data.obligation_type,
        due_date=obs_data.due_date,
        assigned_to=obs_data.assigned_to,
        status=ObligationStatus.PENDING
    )
    db.add(new_obs)
    db.commit()
    db.refresh(new_obs)
    return new_obs

# 2. Get All Obligations
@router.get("/obligations", response_model=List[ObligationResponse], status_code=status.HTTP_200_OK)
def get_all_obligations(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    update_overdue_obligations(db)  # Auto-check for overdue items
    return db.query(Obligation).all()

# 3. Get Obligation by ID
@router.get("/obligations/{obligation_id}", response_model=ObligationResponse, status_code=status.HTTP_200_OK)
def get_obligation_by_id(obligation_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    update_overdue_obligations(db)
    obs = db.query(Obligation).filter(Obligation.id == obligation_id).first()
    if not obs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Obligation Not Found")
    return obs

# 4. Get Obligations for a Contract
@router.get("/contracts/{contract_id}/obligations", response_model=List[ObligationResponse], status_code=status.HTTP_200_OK)
def get_contract_obligations(contract_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    update_overdue_obligations(db)
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Contract ID")
    
    return db.query(Obligation).filter(Obligation.contract_id == contract_id).all()

# 5. Update Obligation
@router.put("/obligations/{obligation_id}", response_model=ObligationResponse, status_code=status.HTTP_200_OK)
def update_obligation(
    obligation_id: int,
    obs_data: ObligationUpdate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    obs = db.query(Obligation).filter(Obligation.id == obligation_id).first()
    if not obs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Obligation Not Found")
    
    update_data = obs_data.dict(exclude_unset=True)
    
    # If they are assigning to a new user, verify the user exists
    if "assigned_to" in update_data:
        user = db.query(User).filter(User.id == update_data["assigned_to"]).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Assigned User")

    for key, value in update_data.items():
        setattr(obs, key, value)
    
    db.commit()
    db.refresh(obs)
    return obs

# 6. Update Status
@router.patch("/obligations/{obligation_id}/status", response_model=ObligationResponse, status_code=status.HTTP_200_OK)
def update_obligation_status(
    obligation_id: int,
    status_data: ObligationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    obs = db.query(Obligation).filter(Obligation.id == obligation_id).first()
    if not obs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Obligation Not Found")
    
    # Prevent invalid transition if it is already completed
    if obs.status == ObligationStatus.COMPLETED and status_data.status != ObligationStatus.COMPLETED:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Status Transition: Cannot change a Completed obligation.")
    
    obs.status = status_data.status
    db.commit()
    db.refresh(obs)
    return obs

# 7. Complete Obligation
@router.post("/obligations/{obligation_id}/complete", response_model=ObligationResponse, status_code=status.HTTP_200_OK)
def complete_obligation(obligation_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    obs = db.query(Obligation).filter(Obligation.id == obligation_id).first()
    if not obs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Obligation Not Found")
    
    obs.status = ObligationStatus.COMPLETED
    obs.completion_date = datetime.utcnow()
    db.commit()
    db.refresh(obs)
    return obs