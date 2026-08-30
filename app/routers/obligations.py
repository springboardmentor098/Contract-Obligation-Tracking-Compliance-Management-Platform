from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.obligation import Obligation
from app.models.contract import Contract
from app.models.user import User
from app.services.notification_service import NotificationService

from app.schemas.obligation import (
    ObligationCreate,
    ObligationUpdate,
    ObligationAssignment,
    ObligationStatusUpdate,
    ObligationProgressUpdate,
    ObligationResponse
)

from app.routers.dependencies import get_current_user


router = APIRouter(
    prefix="/obligations",
    tags=["Obligations"]
)


# ============================================================
# CREATE OBLIGATION
# ============================================================
@router.post(
    "",
    response_model=ObligationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_obligation(
    obligation_data: ObligationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = db.query(Contract).filter(
        Contract.id == obligation_data.contract_id
    ).first()

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    assigned_user = db.query(User).filter(
        User.id == obligation_data.assigned_to
    ).first()

    if assigned_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )

    obligation = Obligation(
        contract_id=obligation_data.contract_id,
        title=obligation_data.title,
        description=obligation_data.description,
        obligation_type=obligation_data.obligation_type,
        due_date=obligation_data.due_date,
        status="Pending",
        progress=0,
        assigned_to=obligation_data.assigned_to
    )

    db.add(obligation)
    db.commit()
    db.refresh(obligation)

# Create obligation due alert notification
    NotificationService.create_obligation_due_alert(
    db=db,
    user_id=obligation.assigned_to,
    contract_id=obligation.contract_id,
    obligation_id=obligation.id,
    message=(
        f"Obligation '{obligation.title}' is due on "
        f"{obligation.due_date}."
    )
)

    return obligation


# ============================================================
# GET ALL OBLIGATIONS
# ============================================================
@router.get(
    "",
    response_model=list[ObligationResponse]
)
def get_obligations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Obligation).all()


# ============================================================
# GET OVERDUE OBLIGATIONS
# IMPORTANT: This must come BEFORE /{obligation_id}
# ============================================================
@router.get(
    "/overdue",
    response_model=list[ObligationResponse]
)
def get_overdue_obligations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()

    obligations = db.query(Obligation).filter(
        Obligation.due_date < today,
        Obligation.status != "Completed"
    ).all()

    for obligation in obligations:
        if obligation.status != "Overdue":
            obligation.status = "Overdue"

        NotificationService.create_obligation_overdue_alert(
            db=db,
            user_id=obligation.assigned_to,
            contract_id=obligation.contract_id,
            obligation_id=obligation.id,
            message=(
                f"Obligation '{obligation.title}' is overdue. "
                f"The due date was {obligation.due_date}."
            )
        )

    db.commit()

    return obligations


# ============================================================
# GET SPECIFIC OBLIGATION
# ============================================================
@router.get(
    "/{obligation_id}",
    response_model=ObligationResponse
)
def get_obligation(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if obligation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found"
        )

    return obligation


# ============================================================
# UPDATE OBLIGATION
# ============================================================
@router.put(
    "/{obligation_id}",
    response_model=ObligationResponse
)
def update_obligation(
    obligation_id: int,
    obligation_data: ObligationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if obligation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found"
        )

    update_data = obligation_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(obligation, field, value)

    obligation.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(obligation)

    return obligation


# ============================================================
# ASSIGN OBLIGATION
# ============================================================
@router.patch(
    "/{obligation_id}/assign",
    response_model=ObligationResponse
)
def assign_obligation(
    obligation_id: int,
    assignment_data: ObligationAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if obligation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found"
        )

    assigned_user = db.query(User).filter(
        User.id == assignment_data.assigned_to
    ).first()

    if assigned_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )

    obligation.assigned_to = assignment_data.assigned_to
    obligation.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(obligation)

    return obligation


# ============================================================
# UPDATE STATUS
# ============================================================
@router.patch(
    "/{obligation_id}/status",
    response_model=ObligationResponse
)
def update_obligation_status(
    obligation_id: int,
    status_data: ObligationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if obligation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found"
        )

    allowed_statuses = {
        "Pending",
        "In Progress",
        "Completed",
        "Overdue"
    }

    if status_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid obligation status"
        )

    obligation.status = status_data.status

    if status_data.status == "Completed":
        obligation.progress = 100

    obligation.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(obligation)

    return obligation


# ============================================================
# UPDATE PROGRESS
# ============================================================
@router.patch(
    "/{obligation_id}/progress",
    response_model=ObligationResponse
)
def update_obligation_progress(
    obligation_id: int,
    progress_data: ObligationProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if obligation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found"
        )

    if progress_data.progress < 0 or progress_data.progress > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Progress must be between 0 and 100"
        )

    obligation.progress = progress_data.progress

    if progress_data.progress == 100:
        obligation.status = "Completed"
    elif progress_data.progress > 0:
        obligation.status = "In Progress"
    else:
        obligation.status = "Pending"

    obligation.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(obligation)

    return obligation


# ============================================================
# COMPLETE OBLIGATION
# ============================================================
@router.post(
    "/{obligation_id}/complete",
    response_model=ObligationResponse
)
def complete_obligation(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if obligation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found"
        )

    obligation.status = "Completed"
    obligation.progress = 100
    obligation.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(obligation)

    return obligation