import os
import uuid
from pathlib import Path
from typing import List
from datetime import datetime

import boto3
from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract, ContractStatus
from app.schemas.contracts import (
    ContractCreate,
    ContractResponse,
    ContractUpdate,
    ContractStatusUpdate,
    ContractAssign,
)
from app.core.roles import UserRole
from app.core.security import get_current_user, normalize_role_name, verify_role
from app.utils.audit import record_audit_log

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


def _allowed_document_type(file_name: str) -> bool:
    allowed_extensions = {".pdf", ".doc", ".docx"}
    return Path(file_name).suffix.lower() in allowed_extensions


def _upload_to_s3(file_name: str, file_content: bytes, content_type: str) -> str:
    bucket_name = os.getenv("AWS_S3_BUCKET")
    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if not bucket_name or not access_key or not secret_key:
        raise RuntimeError("AWS S3 configuration not found")

    s3_client = boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    key = f"contracts/{uuid.uuid4()}-{file_name}"
    s3_client.upload_fileobj(
        __import__("io").BytesIO(file_content),
        bucket_name,
        key,
        ExtraArgs={"ContentType": content_type or "application/octet-stream"},
    )
    return f"https://{bucket_name}.s3.{region}.amazonaws.com/{key}"


def _save_local_fallback(file_name: str, file_content: bytes) -> str:
    safe_name = f"{uuid.uuid4()}-{file_name}"
    destination = UPLOAD_DIR / safe_name
    destination.write_bytes(file_content)
    return f"/uploads/{safe_name}"

# 🛡️ RoleChecker class to enforce permissions
class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = {normalize_role_name(role) for role in allowed_roles if role is not None}

    def __call__(self, current_user: dict = Depends(get_current_user)):
        user_role = normalize_role_name(current_user.get("role"))
        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )

        if user_role not in self.allowed_roles:
            normalized_allowed = {role.lower() for role in self.allowed_roles}
            if user_role.lower() not in normalized_allowed:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to perform this action"
                )

        return current_user

# Create the router
router = APIRouter(prefix="/contracts", tags=["Contracts"])

# Roles setup
require_employee = RoleChecker([UserRole.ADMINISTRATOR, UserRole.EMPLOYEE, "Admin"])
require_admin = RoleChecker(["Admin", "Administrator", "Manager", UserRole.ADMINISTRATOR])
require_standard_user = RoleChecker(["Admin", "Administrator", "Manager", "User"])


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
    record_audit_log(
        db,
        current_user.get("id"),
        "CREATE",
        "Contract",
        new_contract.id,
        f"Created contract {new_contract.contract_number}",
    )
    db.commit()
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
def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_role(["Admin", "Legal Manager"]))
):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    db.delete(contract)
    db.commit()
    return {"detail": f"Contract {contract_id} has been successfully deleted"}


@router.post("/{contract_id}/upload", status_code=status.HTTP_200_OK)
async def upload_contract_document(
    contract_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    if not _allowed_document_type(file.filename or ""):
        raise HTTPException(status_code=400, detail="Only PDF, DOC, and DOCX files are allowed")

    file_content = await file.read()

    try:
        document_url = _upload_to_s3(file.filename or "contract_document", file_content, file.content_type or "application/octet-stream")
    except Exception:
        document_url = _save_local_fallback(file.filename or "contract_document", file_content)

    contract.document_url = document_url
    db.commit()
    db.refresh(contract)

    return {"detail": "Document uploaded successfully", "document_url": document_url, "contract_id": contract.id}


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
    record_audit_log(
        db,
        current_user.get("id"),
        "UPDATE",
        "Contract",
        contract.id,
        f"Updated contract {contract.contract_number}",
    )
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