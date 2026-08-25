from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies import get_current_user
from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.user import User
from app.schemas.obligation import (
    ObligationCreate,
    ObligationResponse,
    ObligationUpdate,
    ObligationStatusUpdate
)


router = APIRouter(
    tags=["Obligations"]
)


# =========================
# CREATE OBLIGATION
# =========================

@router.post(
    "/obligations",
    response_model=ObligationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_obligation(
    obligation_data: ObligationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    contract = db.query(Contract).filter(
        Contract.id == obligation_data.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    assigned_user = db.query(User).filter(
        User.id == obligation_data.assigned_to
    ).first()

    if not assigned_user:
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
        assigned_to=obligation_data.assigned_to,
        status="Pending"
    )

    db.add(obligation)
    db.commit()
    db.refresh(obligation)

    return obligation


# =========================
# GET ALL OBLIGATIONS
# =========================

@router.get(
    "/obligations",
    response_model=list[ObligationResponse],
    status_code=status.HTTP_200_OK
)
def get_obligations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return db.query(Obligation).all()


# =========================
# GET OBLIGATION BY ID
# =========================

@router.get(
    "/obligations/{obligation_id}",
    response_model=ObligationResponse,
    status_code=status.HTTP_200_OK
)
def get_obligation(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found"
        )

    return obligation


# =========================
# GET CONTRACT OBLIGATIONS
# =========================

@router.get(
    "/contracts/{contract_id}/obligations",
    response_model=list[ObligationResponse],
    status_code=status.HTTP_200_OK
)
def get_contract_obligations(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return db.query(Obligation).filter(
        Obligation.contract_id == contract_id
    ).all()


# =========================
# UPDATE OBLIGATION
# =========================

@router.put(
    "/obligations/{obligation_id}",
    response_model=ObligationResponse,
    status_code=status.HTTP_200_OK
)
def update_obligation(
    obligation_id: int,
    obligation_data: ObligationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found"
        )

    if obligation.assigned_to != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this obligation"
        )

    if obligation_data.assigned_to is not None:
        assigned_user = db.query(User).filter(
            User.id == obligation_data.assigned_to
        ).first()

        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found"
            )

    update_data = obligation_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(obligation, field, value)

    db.commit()
    db.refresh(obligation)

    return obligation


# =========================
# UPDATE OBLIGATION STATUS
# =========================

@router.patch(
    "/obligations/{obligation_id}/status",
    response_model=ObligationResponse,
    status_code=status.HTTP_200_OK
)
def update_obligation_status(
    obligation_id: int,
    status_data: ObligationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found"
        )

    if obligation.assigned_to != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this obligation"
        )

    current_status = obligation.status
    new_status = status_data.status

    valid_transitions = {
        "Pending": ["In Progress"],
        "In Progress": ["Completed"],
        "Completed": [],
        "Delayed": ["In Progress", "Completed"],
        "Overdue": ["In Progress", "Completed"]
    }

    if new_status not in valid_transitions.get(
        current_status,
        []
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from {current_status} to {new_status}"
        )

    obligation.status = new_status

    db.commit()
    db.refresh(obligation)

    return obligation


# =========================
# COMPLETE OBLIGATION
# =========================

@router.post(
    "/obligations/{obligation_id}/complete",
    response_model=ObligationResponse,
    status_code=status.HTTP_200_OK
)
def complete_obligation(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found"
        )

    if obligation.assigned_to != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to complete this obligation"
        )

    if obligation.status != "In Progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only In Progress obligations can be completed"
        )

    obligation.status = "Completed"
    obligation.completion_date = date.today()

    db.commit()
    db.refresh(obligation)

    return obligation