from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.contract import Contract
from app.schemas.contracts import ContractCreate, ContractResponse
from app.core.roles import UserRole
from typing import List

#  Import the correct auth function
from app.core.security import get_current_user

#  RoleChecker class to enforce permissions
class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    #  Replaced broken require_auth with get_current_user
    def __call__(self, current_user: dict = Depends(get_current_user)):
        # Check if the user's role is in the allowed list
        print("TOKEN PAYLOAD IS:", current_user)
        if current_user.get("role") not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="You do not have permission to perform this action"
            )
        return current_user

# Create the router
router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)

# Roles setup - Updated to match your database exactly!
require_employee = RoleChecker([UserRole.ADMINISTRATOR, UserRole.EMPLOYEE])
require_admin = RoleChecker(["Administrator", "Manager"]) 
require_standard_user = RoleChecker(["Administrator", "Manager", "User"])

# API 1: Create a Contract (POST /contracts)
@router.post("/", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
def create_contract(
    contract_data: ContractCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    # 1. Check for duplicate contract number
    existing_contract = db.query(Contract).filter(Contract.contract_number == contract_data.contract_number).first()
    if existing_contract:
        raise HTTPException(status_code=400, detail="Contract number already exists")

    # 2. Create the contract
    new_contract = Contract(
        title=contract_data.title,
        contract_number=contract_data.contract_number,
        category=contract_data.category,
        description=contract_data.description,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        created_by=current_user["id"]  
    )

    # 3. Save to PostgreSQL
    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)
    
    return new_contract

@router.get("/", response_model=List[ContractResponse], status_code=status.HTTP_200_OK)
def get_all_contracts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user) # 👇 Fixed!
):
    # Fetch all contracts from the database
    contracts = db.query(Contract).all()
    
    return contracts

@router.get("/{contract_id}", response_model=ContractResponse, status_code=status.HTTP_200_OK)
def get_contract_by_id(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user) # 👇 Fixed!
):
    # 1. Search for the contract by its ID
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    
    # 2. If it does not exist, return a 404 Not Found error
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Contract not found"
        )
        
    # 3. Return the contract details
    return contract

@router.put("/{contract_id}", response_model=ContractResponse, status_code=status.HTTP_200_OK)
def update_contract(
    contract_id: int,
    contract_data: ContractCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)  # 🔒 Locked to Admins/Managers
):
    # 1. Search for the existing contract
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    
    # 2. Return 404 if it does not exist
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Contract not found"
        )
        
    # 3. Update the contract details
    contract.title = contract_data.title
    contract.contract_number = contract_data.contract_number
    contract.category = contract_data.category
    contract.description = contract_data.description
    contract.start_date = contract_data.start_date
    contract.end_date = contract_data.end_date
    
    # 4. Save the changes to the database
    db.commit()
    db.refresh(contract)
    
    return contract

@router.delete("/{contract_id}", status_code=status.HTTP_200_OK)
def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)  # 🔒 Locked to Admins/Managers
):
    # 1. Search for the existing contract
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    
    # 2. Return 404 if it does not exist
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Contract not found"
        )
        
    # 3. Delete from the database
    db.delete(contract)
    db.commit()
    
    return {"detail": f"Contract {contract_id} has been successfully deleted"}