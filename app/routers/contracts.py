from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database.database import get_db
from app.models.contract import Contract, ContractStatus
from app.schemas.contracts import (
    ContractCreate, 
    ContractResponse, 
    ContractUpdate, 
    ContractStatusUpdate, 
    ContractAssign
)
from app.core.roles import UserRole
from app.core.security import get_current_user

# 🛡️ RoleChecker class to enforce permissions
class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="You do not have permission to perform this action"
            )
        return current_user

# Create the router
router = APIRouter(prefix="/contracts", tags=["Contracts"])

# Roles setup
require_employee = RoleChecker([UserRole.ADMINISTRATOR, UserRole.EMPLOYEE])
require_admin = RoleChecker(["Administrator", "Manager"]) 
require_standard_user = RoleChecker(["Administrator", "Manager", "User"])


# ==========================================
# 📝 CORE CRUD APIs
# ==========================================

@router.post("/", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
def create_contract(
    contract_data: ContractCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    existing_contract = db.query(Contract).filter(Contract.contract_number == contract_data.contract_number).first()
    if existing_contract:
        raise HTTPException(status_code=400, detail="Contract number already exists")

    new_contract = Contract(
        title=contract_data.title,
        contract_number=contract_data.contract_number,
        category=contract_data.category,
        description=contract_data.description,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        created_by=current_user["id"]  
    )
    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)
    return new_contract

@router.get("/", response_model=List[ContractResponse], status_code=status.HTTP_200_OK)
def get_all_contracts(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return db.query(Contract).all()

@router.get("/{contract_id}", response_model=ContractResponse, status_code=status.HTTP_200_OK)
def get_contract_by_id(contract_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return contract

@router.delete("/{contract_id}", status_code=status.HTTP_200_OK)
def delete_contract(contract_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    db.delete(contract)
    db.commit()
    return {"detail": f"Contract {contract_id} has been successfully deleted"}


# ==========================================
# 🚀 SPRINT 8: WORKFLOW & APPROVAL APIs
# ==========================================

# 1. Update Contract Details
@router.put("/{contract_id}", response_model=ContractResponse, status_code=status.HTTP_200_OK)
def update_contract(
    contract_id: int,
    contract_data: ContractUpdate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
        
    # Update only the fields the user provided
    update_data = contract_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(contract, key, value)
    
    db.commit()
    db.refresh(contract)
    return contract

# 2. Submit for Review (Draft -> Under Review)
@router.post("/{contract_id}/submit-review", response_model=ContractResponse, status_code=status.HTTP_200_OK)
def submit_for_review(contract_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    if contract.status != ContractStatus.DRAFT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only Draft contracts can be submitted")
    
    contract.status = ContractStatus.UNDER_REVIEW
    contract.reviewed_at = datetime.utcnow()
    db.commit()
    db.refresh(contract)
    return contract

# 3. Approve Contract (Under Review -> Approved)
@router.post("/{contract_id}/approve", response_model=ContractResponse, status_code=status.HTTP_200_OK)
def approve_contract(contract_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    if contract.status != ContractStatus.UNDER_REVIEW:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only Under Review contracts can be approved")
    
    contract.status = ContractStatus.APPROVED
    contract.approved_at = datetime.utcnow()
    db.commit()
    db.refresh(contract)
    return contract

# 4. Activate Contract (Approved -> Active)
@router.post("/{contract_id}/activate", response_model=ContractResponse, status_code=status.HTTP_200_OK)
def activate_contract(contract_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    if contract.status != ContractStatus.APPROVED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only Approved contracts can be activated")
    
    contract.status = ContractStatus.ACTIVE
    db.commit()
    db.refresh(contract)
    return contract

# 5. Assign Contract to a User
@router.patch("/{contract_id}/assign", response_model=ContractResponse, status_code=status.HTTP_200_OK)
def assign_contract(contract_id: int, assign_data: ContractAssign, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    
    contract.assigned_to = assign_data.assigned_to
    db.commit()
    db.refresh(contract)
    return contract

# 6. Manual Status Override 
@router.patch("/{contract_id}/status", response_model=ContractResponse, status_code=status.HTTP_200_OK)
def update_contract_status(contract_id: int, status_data: ContractStatusUpdate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    
    contract.status = status_data.status
    db.commit()
    db.refresh(contract)
    return contract