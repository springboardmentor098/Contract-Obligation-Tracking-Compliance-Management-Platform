from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.obligation import Obligation
from app.models.contract import Contract
from app.models.user import User
from app.schemas.obligation_schema import (
    ObligationCreate,
    ObligationUpdate,
    ObligationStatusUpdate,
    ObligationResponse
)
from app.core.auth import get_current_user
from app.core.role_checker import require_non_viewer
from app.services.activity_service import log_activity

router = APIRouter(
    prefix="/obligations",
    tags=["Obligations"],
    dependencies=[Depends(require_non_viewer)],
)


# ---------------- CREATE OBLIGATION ----------------

@router.post(
    "",
    response_model=ObligationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_obligation(
    obligation_data: ObligationCreate,
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(
        Contract.id == obligation_data.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found"
        )

    user = db.query(User).filter(
        User.id == obligation_data.assigned_to
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Assigned user not found"
        )

    obligation = Obligation(
        contract_id=obligation_data.contract_id,
        title=obligation_data.title,
        description=obligation_data.description,
        obligation_type=obligation_data.obligation_type,
        priority=obligation_data.priority,
        due_date=obligation_data.due_date,
        assigned_to=obligation_data.assigned_to,
        status="Pending"
    )

    db.add(obligation)
    db.commit()
    db.refresh(obligation)

    # Automatically record CREATE_OBLIGATION activity log
    log_activity(
        db=db,
        action="CREATE_OBLIGATION",
        entity_type="Obligation",
        entity_id=obligation.id,
        contract_id=obligation.contract_id,
        description=f"Created obligation '{obligation.title}' on contract '{contract.title}'",
        user=current_user,
        request=request,
    )

    return obligation


# ---------------- GET ALL OBLIGATIONS ----------------

@router.get(
    "",
    response_model=list[ObligationResponse]
)
def get_obligations(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Obligation).all()


# ---------------- GET OBLIGATION BY ID ----------------

@router.get(
    "/{obligation_id}",
    response_model=ObligationResponse
)
def get_obligation(
    obligation_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail="Obligation not found"
        )

    return obligation


# ---------------- GET OBLIGATIONS FOR A CONTRACT ----------------

@router.get(
    "/contract/{contract_id}",
    response_model=list[ObligationResponse]
)
def get_contract_obligations(
    contract_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found"
        )

    return db.query(Obligation).filter(
        Obligation.contract_id == contract_id
    ).all()


# ---------------- UPDATE OBLIGATION ----------------

@router.put(
    "/{obligation_id}",
    response_model=ObligationResponse
)
def update_obligation(
    obligation_id: int,
    obligation_data: ObligationUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail="Obligation not found"
        )

    update_data = obligation_data.model_dump(exclude_unset=True)

    if "assigned_to" in update_data:
        user = db.query(User).filter(
            User.id == update_data["assigned_to"]
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Assigned user not found"
            )

    old_status = obligation.status

    for key, value in update_data.items():
        setattr(obligation, key, value)

    db.commit()
    db.refresh(obligation)

    if update_data.get("status") == "Completed" and old_status != "Completed":
        log_activity(
            db=db,
            action="COMPLETE_OBLIGATION",
            entity_type="Obligation",
            entity_id=obligation.id,
            contract_id=obligation.contract_id,
            description=f"Completed obligation '{obligation.title}'",
            user=current_user,
            request=request,
        )
    else:
        log_activity(
            db=db,
            action="UPDATE_OBLIGATION",
            entity_type="Obligation",
            entity_id=obligation.id,
            contract_id=obligation.contract_id,
            description=f"Updated obligation '{obligation.title}'",
            user=current_user,
            request=request,
        )

    return obligation


# ---------------- UPDATE STATUS ----------------

@router.patch(
    "/{obligation_id}/status",
    response_model=ObligationResponse
)
def update_status(
    obligation_id: int,
    status_data: ObligationStatusUpdate,
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail="Obligation not found"
        )

    workflow = {
        "Pending": ["In Progress"],
        "In Progress": ["Completed"],
        "Completed": [],
        "Delayed": ["Completed"],
        "Overdue": ["Completed"]
    }

    current = obligation.status
    new = status_data.status

    if new not in workflow.get(current, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition from '{current}' to '{new}'"
        )

    obligation.status = new

    if new == "Completed":
        obligation.completion_date = date.today()

    db.commit()
    db.refresh(obligation)

    # Automatically record COMPLETE_OBLIGATION activity log if completed
    if new == "Completed":
        log_activity(
            db=db,
            action="COMPLETE_OBLIGATION",
            entity_type="Obligation",
            entity_id=obligation.id,
            contract_id=obligation.contract_id,
            description=f"Completed obligation '{obligation.title}'",
            user=current_user,
            request=request,
        )
    else:
        log_activity(
            db=db,
            action="UPDATE_OBLIGATION_STATUS",
            entity_type="Obligation",
            entity_id=obligation.id,
            contract_id=obligation.contract_id,
            description=f"Updated obligation '{obligation.title}' status to {new}",
            user=current_user,
            request=request,
        )

    return obligation


@router.delete("/{obligation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_obligation(
    obligation_id: int,
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    obligation = db.query(Obligation).filter(Obligation.id == obligation_id).first()
    if not obligation:
        raise HTTPException(status_code=404, detail="Obligation not found")
    
    title = obligation.title
    contract_id = obligation.contract_id

    db.delete(obligation)
    db.commit()

    log_activity(
        db=db,
        action="DELETE_OBLIGATION",
        entity_type="Obligation",
        entity_id=obligation_id,
        contract_id=contract_id,
        description=f"Deleted obligation '{title}'",
        user=current_user,
        request=request,
    )