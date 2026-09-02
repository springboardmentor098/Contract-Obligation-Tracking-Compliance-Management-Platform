from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime

from app.database.database import get_db
from app.models.all_models import Renewal, Contract, User, RenewalStatus
from app.schemas.renewal import (
    RenewalCreate,
    RenewalResponse,
    RenewalUpdate,
    RenewalStatusUpdate
)
from app.core.security import get_current_user

#  RoleChecker to enforce permissions
class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    def __call__(self, current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient Permission")
        return current_user

require_admin = RoleChecker(["Administrator", "Manager"]) 

router = APIRouter(tags=["Renewals"])

# ==========================================
#  RENEWAL APIs
# ==========================================

# 1. Create Renewal
@router.post("/renewals", response_model=RenewalResponse, status_code=status.HTTP_201_CREATED)
def create_renewal(
    ren_data: RenewalCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    if ren_data.new_expiry_date < ren_data.renewal_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Date Range: New expiry date cannot be earlier than renewal date.")

    contract = db.query(Contract).filter(Contract.id == ren_data.contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract Not Found")
    
    assigned_user = db.query(User).filter(User.id == ren_data.assigned_to).first()
    if not assigned_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid User")
    
    new_renewal = Renewal(
        contract_id=ren_data.contract_id,
        renewal_date=ren_data.renewal_date,
        previous_expiry_date=ren_data.previous_expiry_date,
        new_expiry_date=ren_data.new_expiry_date,
        assigned_to=ren_data.assigned_to,
        notes=ren_data.notes,
        status=RenewalStatus.UPCOMING
    )
    db.add(new_renewal)
    db.commit()
    db.refresh(new_renewal)
    return new_renewal

# 2. Get All Renewals
@router.get("/renewals", response_model=List[RenewalResponse], status_code=status.HTTP_200_OK)
def get_all_renewals(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return db.query(Renewal).all()

# 3. Get Renewal by ID
@router.get("/renewals/{renewal_id}", response_model=RenewalResponse, status_code=status.HTTP_200_OK)
def get_renewal_by_id(renewal_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    renewal = db.query(Renewal).filter(Renewal.id == renewal_id).first()
    if not renewal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Renewal Not Found")
    return renewal

# 4. Get Renewals for a Contract
@router.get("/contracts/{contract_id}/renewals", response_model=List[RenewalResponse], status_code=status.HTTP_200_OK)
def get_contract_renewals(contract_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract Not Found")
    
    return db.query(Renewal).filter(Renewal.contract_id == contract_id).all()

# 5. Update Renewal
@router.put("/renewals/{renewal_id}", response_model=RenewalResponse, status_code=status.HTTP_200_OK)
def update_renewal(
    renewal_id: int,
    ren_data: RenewalUpdate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    renewal = db.query(Renewal).filter(Renewal.id == renewal_id).first()
    if not renewal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Renewal Not Found")
    
    update_data = ren_data.dict(exclude_unset=True)
    
    if "assigned_to" in update_data:
        user = db.query(User).filter(User.id == update_data["assigned_to"]).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid User")

    for key, value in update_data.items():
        setattr(renewal, key, value)
    
    db.commit()
    db.refresh(renewal)
    return renewal

# 6. Update Renewal Status
@router.patch("/renewals/{renewal_id}/status", response_model=RenewalResponse, status_code=status.HTTP_200_OK)
def update_renewal_status(
    renewal_id: int,
    status_data: RenewalStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    renewal = db.query(Renewal).filter(Renewal.id == renewal_id).first()
    if not renewal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Renewal Not Found")
    
    if renewal.status == RenewalStatus.RENEWED and status_data.status != RenewalStatus.RENEWED:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Status Transition: Cannot change a completed renewal.")
    
    renewal.status = status_data.status
    db.commit()
    db.refresh(renewal)
    return renewal

# 7. Complete Renewal
@router.post("/renewals/{renewal_id}/renew", response_model=RenewalResponse, status_code=status.HTTP_200_OK)
def complete_renewal(renewal_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    renewal = db.query(Renewal).filter(Renewal.id == renewal_id).first()
    if not renewal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Renewal Not Found")
    
    # Update Renewal Status
    renewal.status = RenewalStatus.RENEWED
    
    # Update Associated Contract's end date
    contract = db.query(Contract).filter(Contract.id == renewal.contract_id).first()
    if contract:
        contract.end_date = renewal.new_expiry_date
    
    db.commit()
    db.refresh(renewal)
    return renewal

# ==========================================
# 📊 DETECTION LOGIC (Upcoming & Expired)
# ==========================================
@router.get("/monitoring/expiries", status_code=status.HTTP_200_OK)
def check_contract_expiries(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Scans all contracts to identify which ones are expired or approaching expiry."""
    contracts = db.query(Contract).all()
    today = date.today()
    
    expired = []
    upcoming = []
    
    for c in contracts:
        if not c.end_date:
            continue
            
        days_left = (c.end_date - today).days
        
        if days_left < 0:
            expired.append({
                "contract_id": c.id, 
                "title": c.title, 
                "expiry_date": c.end_date, 
                "days_overdue": abs(days_left),
                "status": "Expired"
            })
        elif 0 <= days_left <= 90:
            upcoming.append({
                "contract_id": c.id, 
                "title": c.title, 
                "expiry_date": c.end_date, 
                "days_remaining": days_left, 
                "status": "Upcoming"
            })
            
    return {
        "expired_contracts": expired,
        "upcoming_renewals": upcoming
    }