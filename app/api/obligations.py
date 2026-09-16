from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.obligation import Obligation
from app.schemas.obligation_schema import (
    ObligationCreate,
    ObligationRead,
    ObligationStatusUpdate,
    ObligationUpdate,
)
from app.core.dependencies import require_permission
from app.core.permissions import Permission
from app.services.audit_service import create_audit_log
from app.services.obligation_service import mark_overdue_obligations


router = APIRouter(
    prefix="/obligations",
    tags=["Obligations"],
)


# =========================================================
# CREATE OBLIGATION
# =========================================================

@router.post(
    "",
    response_model=ObligationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_obligation(
    obligation_data: ObligationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.CREATE_OBLIGATION)
    ),
):
    # -----------------------------------------------------
    # Validate contract
    # -----------------------------------------------------

    contract = (
        db.query(Contract)
        .filter(Contract.id == obligation_data.contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    # -----------------------------------------------------
    # Create obligation
    # -----------------------------------------------------

    obligation = Obligation(
        contract_id=obligation_data.contract_id,
        title=obligation_data.title,
        description=obligation_data.description,
        due_date=obligation_data.due_date,
        priority=obligation_data.priority,
        responsible_party=obligation_data.responsible_party,
        status="pending",
    )

    db.add(obligation)
    db.commit()
    db.refresh(obligation)

    # -----------------------------------------------------
    # Audit log
    # -----------------------------------------------------

    create_audit_log(
        db=db,
        user_id=int(current_user["sub"]),
        contract_id=obligation.contract_id,
        action="Created obligation",
        entity_type="Obligation",
        entity_id=obligation.id,
        details=f"Created obligation '{obligation.title}'",
    )

    db.commit()

    return obligation


# =========================================================
# LIST ALL OBLIGATIONS
# =========================================================

@router.get(
    "",
    response_model=list[ObligationRead],
)
def list_obligations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.READ_OBLIGATION)
    ),
):
    return (
        db.query(Obligation)
        .order_by(Obligation.due_date.asc())
        .all()
    )


# =========================================================
# GET SINGLE OBLIGATION
# =========================================================

@router.get(
    "/{obligation_id}",
    response_model=ObligationRead,
)
def get_obligation(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.READ_OBLIGATION)
    ),
):
    obligation = (
        db.query(Obligation)
        .filter(Obligation.id == obligation_id)
        .first()
    )

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found",
        )

    return obligation


# =========================================================
# UPDATE OBLIGATION
# =========================================================

@router.put(
    "/{obligation_id}",
    response_model=ObligationRead,
)
def update_obligation(
    obligation_id: int,
    obligation_data: ObligationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.UPDATE_OBLIGATION)
    ),
):
    obligation = (
        db.query(Obligation)
        .filter(Obligation.id == obligation_id)
        .first()
    )

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found",
        )

    # -----------------------------------------------------
    # Apply updates
    # -----------------------------------------------------

    update_data = obligation_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(obligation, field, value)

    db.commit()
    db.refresh(obligation)

    # -----------------------------------------------------
    # Audit log
    # -----------------------------------------------------

    create_audit_log(
        db=db,
        user_id=int(current_user["sub"]),
        contract_id=obligation.contract_id,
        action="Updated obligation",
        entity_type="Obligation",
        entity_id=obligation.id,
        details=f"Updated obligation '{obligation.title}'",
    )

    db.commit()

    return obligation


# =========================================================
# UPDATE OBLIGATION STATUS
# =========================================================

@router.patch(
    "/{obligation_id}/status",
    response_model=ObligationRead,
)
def update_obligation_status(
    obligation_id: int,
    status_data: ObligationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.UPDATE_OBLIGATION)
    ),
):
    obligation = (
        db.query(Obligation)
        .filter(Obligation.id == obligation_id)
        .first()
    )

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found",
        )

    # -----------------------------------------------------
    # Determine status transition
    # -----------------------------------------------------

    current_status = obligation.status
    new_status = status_data.status.lower()

    allowed_transitions = {
        "pending": {
            "in_progress",
            "overdue",
        },
        "in_progress": {
            "completed",
            "overdue",
        },
        "overdue": {
            "in_progress",
        },
        "completed": set(),
    }

    allowed_next_statuses = allowed_transitions.get(
        current_status.lower(),
        set(),
    )

    if new_status not in allowed_next_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid obligation status transition: "
                f"{current_status} -> {new_status}"
            ),
        )

    # -----------------------------------------------------
    # Update status
    # -----------------------------------------------------

    obligation.status = new_status

    db.commit()
    db.refresh(obligation)

    # -----------------------------------------------------
    # Audit log
    # -----------------------------------------------------

    create_audit_log(
        db=db,
        user_id=int(current_user["sub"]),
        contract_id=obligation.contract_id,
        action="Changed obligation status",
        entity_type="Obligation",
        entity_id=obligation.id,
        details=(
            f"Changed obligation '{obligation.title}' "
            f"status from '{current_status}' to '{new_status}'"
        ),
    )

    db.commit()

    return obligation


# =========================================================
# SCAN AND MARK OVERDUE OBLIGATIONS
# =========================================================

@router.post(
    "/scan-overdue",
)
def scan_overdue_obligations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.UPDATE_OBLIGATION)
    ),
):
    updated_count = mark_overdue_obligations(db)

    return {
        "message": "Overdue obligation scan completed",
        "updated_count": updated_count,
    }


# =========================================================
# DELETE OBLIGATION
# =========================================================

@router.delete(
    "/{obligation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_obligation(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.DELETE_OBLIGATION)
    ),
):
    obligation = (
        db.query(Obligation)
        .filter(Obligation.id == obligation_id)
        .first()
    )

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found",
        )

    # -----------------------------------------------------
    # Store values before deleting the obligation
    # -----------------------------------------------------

    obligation_title = obligation.title
    contract_id = obligation.contract_id

    # -----------------------------------------------------
    # Create audit log BEFORE deletion
    # -----------------------------------------------------

    create_audit_log(
        db=db,
        user_id=int(current_user["sub"]),
        contract_id=contract_id,
        action="Deleted obligation",
        entity_type="Obligation",
        entity_id=obligation.id,
        details=f"Deleted obligation '{obligation_title}'",
    )

    # -----------------------------------------------------
    # Delete obligation
    # -----------------------------------------------------

    db.delete(obligation)

    db.commit()

    return None