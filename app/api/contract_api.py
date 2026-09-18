from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.role_checker import RoleChecker
from app.database.database import get_db
from app.models.activity import Activity
from app.models.contract import Contract
from app.models.notification import Notification
from app.models.obligation import Obligation
from app.models.renewal import Renewal
from app.schemas.contract_schema import (
    ContractAssignment,
    ContractCreate,
    ContractResponse,
    ContractStatusUpdate,
    ContractUpdate,
)
from app.services.activity_service import log_activity

router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)


@router.post(
    "",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED
)
@router.post(
    "/",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False
)
def create_contract(
    contract_data: ContractCreate,
    request: Request,
    current_user=Depends(RoleChecker(["Admin", "Legal Manager", "Contract Manager"])),
    db: Session = Depends(get_db)
):
    # Check duplicate contract number
    existing = db.query(Contract).filter(
        Contract.contract_number == contract_data.contract_number
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Contract number already exists"
        )

    contract = Contract(
        title=contract_data.title,
        contract_number=contract_data.contract_number,
        category=contract_data.category,
        description=contract_data.description,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        department=contract_data.department,
        assigned_to=contract_data.assigned_to,
        status="Draft",
        created_by=current_user.id
    )

    db.add(contract)
    db.commit()
    db.refresh(contract)

    # Automatically record CREATE_CONTRACT activity log
    log_activity(
        db=db,
        action="CREATE_CONTRACT",
        entity_type="Contract",
        entity_id=contract.id,
        contract_id=contract.id,
        description=f"Created contract '{contract.title}' ({contract.contract_number})",
        user=current_user,
        request=request,
    )

    return contract


@router.get(
    "/",
    response_model=list[ContractResponse],
    status_code=status.HTTP_200_OK
)
def get_contracts(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contracts = db.query(Contract).all()
    return contracts


@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def get_contract(
    contract_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return contract


@router.put(
    "/{contract_id}",
    response_model=ContractResponse
)
def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    request: Request,
    current_user=Depends(RoleChecker(["Admin", "Legal Manager", "Contract Manager"])),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    if "contract_number" in contract_data.model_fields_set:
        existing = db.query(Contract).filter(
            Contract.contract_number == contract_data.contract_number,
            Contract.id != contract_id,
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Contract number already exists")

    update_data = contract_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(contract, key, value)

    db.commit()
    db.refresh(contract)

    # Automatically record UPDATE_CONTRACT activity log
    log_activity(
        db=db,
        action="UPDATE_CONTRACT",
        entity_type="Contract",
        entity_id=contract.id,
        contract_id=contract.id,
        description=f"Updated contract '{contract.title}' ({contract.contract_number})",
        user=current_user,
        request=request,
    )

    return contract


@router.delete("/{contract_id}", status_code=status.HTTP_200_OK)
def delete_contract(
    contract_id: int,
    request: Request,
    current_user=Depends(RoleChecker(["Administrator", "Legal Manager"])),
    db: Session = Depends(get_db),
):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    title = contract.title
    contract_number = contract.contract_number

    db.query(Activity).filter(Activity.contract_id == contract_id).delete(synchronize_session=False)
    db.query(Notification).filter(Notification.contract_id == contract_id).delete(synchronize_session=False)
    db.query(Obligation).filter(Obligation.contract_id == contract_id).delete(synchronize_session=False)
    db.query(Renewal).filter(Renewal.contract_id == contract_id).delete(synchronize_session=False)
    db.delete(contract)
    db.commit()

    # Automatically record DELETE_CONTRACT activity log with contract_id=None so it persists
    log_activity(
        db=db,
        action="DELETE_CONTRACT",
        entity_type="Contract",
        entity_id=contract_id,
        contract_id=None,
        description=f"Deleted contract '{title}' ({contract_number})",
        user=current_user,
        request=request,
    )

    return {"message": "Contract deleted successfully"}


@router.patch(
    "/{contract_id}/status",
    response_model=ContractResponse
)
def change_status(
    contract_id: int,
    status_data: ContractStatusUpdate,
    request: Request,
    current_user=Depends(RoleChecker(["Administrator", "Legal Manager"])),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    workflow = {
        "Draft": ["Under Review"],
        "Under Review": ["Approved", "Draft", "Rejected"],
        "Approved": ["Active"],
        "Active": ["Expired", "Terminated"],
        "Expired": [],
        "Terminated": ["Archived"],
        "Archived": [],
        "Rejected": ["Draft"],
    }

    if status_data.status not in workflow.get(contract.status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status transition"
        )

    old_status = contract.status
    contract.status = status_data.status

    if status_data.status == "Under Review":
        contract.reviewed_at = datetime.utcnow()
    elif status_data.status == "Approved":
        contract.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    # Automatically record status transition
    if status_data.status == "Approved":
        action = "APPROVE_CONTRACT"
        desc = f"Approved contract '{contract.title}' ({contract.contract_number})"
    elif status_data.status in ["Rejected", "Draft"] and old_status == "Under Review":
        action = "REJECT_CONTRACT"
        desc = f"Rejected contract '{contract.title}' ({contract.contract_number})"
    else:
        action = "UPDATE_CONTRACT_STATUS"
        desc = f"Changed status of contract '{contract.title}' to {contract.status}"

    log_activity(
        db=db,
        action=action,
        entity_type="Contract",
        entity_id=contract.id,
        contract_id=contract.id,
        description=desc,
        user=current_user,
        request=request,
    )

    return contract


@router.post(
    "/{contract_id}/submit-review",
    response_model=ContractResponse
)
def submit_review(
    contract_id: int,
    request: Request,
    current_user=Depends(RoleChecker(["Admin", "Legal Manager", "Contract Manager"])),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(404, "Contract not found")

    if contract.status != "Draft":
        raise HTTPException(400, "Only Draft contracts can be submitted")

    if contract.created_by != current_user.id and contract.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the contract owner or assignee can submit it for review"
        )

    contract.status = "Under Review"
    contract.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    log_activity(
        db=db,
        action="SUBMIT_REVIEW",
        entity_type="Contract",
        entity_id=contract.id,
        contract_id=contract.id,
        description=f"Submitted contract '{contract.title}' for review",
        user=current_user,
        request=request,
    )

    return contract


@router.post(
    "/{contract_id}/approve",
    response_model=ContractResponse
)
def approve_contract(
    contract_id: int,
    request: Request,
    current_user=Depends(RoleChecker(["Administrator", "Legal Manager"])),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(404, "Contract not found")

    if contract.status != "Under Review":
        raise HTTPException(400, "Contract must be Under Review")

    contract.status = "Approved"
    contract.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(contract)

    # Automatically record APPROVE_CONTRACT activity log
    log_activity(
        db=db,
        action="APPROVE_CONTRACT",
        entity_type="Contract",
        entity_id=contract.id,
        contract_id=contract.id,
        description=f"Approved contract '{contract.title}' ({contract.contract_number})",
        user=current_user,
        request=request,
    )

    return contract


@router.post(
    "/{contract_id}/reject",
    response_model=ContractResponse
)
def reject_contract(
    contract_id: int,
    request: Request,
    current_user=Depends(RoleChecker(["Administrator", "Legal Manager"])),
    db: Session = Depends(get_db)
):
    """Rejects a contract that is Under Review, moving it back to Draft."""
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(404, "Contract not found")

    if contract.status != "Under Review":
        raise HTTPException(400, "Only contracts Under Review can be rejected")

    contract.status = "Draft"

    db.commit()
    db.refresh(contract)

    # Automatically record REJECT_CONTRACT activity log
    log_activity(
        db=db,
        action="REJECT_CONTRACT",
        entity_type="Contract",
        entity_id=contract.id,
        contract_id=contract.id,
        description=f"Rejected contract '{contract.title}' ({contract.contract_number})",
        user=current_user,
        request=request,
    )

    return contract


@router.post(
    "/{contract_id}/activate",
    response_model=ContractResponse
)
def activate_contract(
    contract_id: int,
    request: Request,
    current_user=Depends(RoleChecker(["Administrator", "Legal Manager"])),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(404, "Contract not found")

    if contract.status != "Approved":
        raise HTTPException(400, "Only Approved contracts can be activated")

    contract.status = "Active"

    db.commit()
    db.refresh(contract)

    log_activity(
        db=db,
        action="ACTIVATE_CONTRACT",
        entity_type="Contract",
        entity_id=contract.id,
        contract_id=contract.id,
        description=f"Activated contract '{contract.title}' ({contract.contract_number})",
        user=current_user,
        request=request,
    )

    return contract


@router.patch(
    "/{contract_id}/assign",
    response_model=ContractResponse
)
def assign_contract(
    contract_id: int,
    assignment: ContractAssignment,
    request: Request,
    current_user=Depends(RoleChecker(["Administrator", "Legal Manager"])),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(404, "Contract not found")

    contract.assigned_to = assignment.assigned_to

    db.commit()
    db.refresh(contract)

    log_activity(
        db=db,
        action="ASSIGN_CONTRACT",
        entity_type="Contract",
        entity_id=contract.id,
        contract_id=contract.id,
        description=f"Assigned contract '{contract.title}' to user #{assignment.assigned_to}",
        user=current_user,
        request=request,
    )

    return contract
