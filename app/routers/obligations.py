from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.contracts import Contract
from app.schemas.obligation import (
    ObligationCreate,
    ObligationUpdate,
    ObligationStatusUpdate,
    ObligationResponse,
)
from app.services.obligation import (
    create_obligation,
    get_all_obligations,
    get_obligation_by_id,
    update_obligation,
    update_obligation_status,
    complete_obligation,
)

router = APIRouter(
    prefix="/obligations",
    tags=["Obligations"]
)


# CREATE OBLIGATION
@router.post(
    "",
    response_model=ObligationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_obligation_api(
    data: ObligationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = db.query(Contract).filter(
        Contract.id == data.contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail="Contract not found"
        )

    assigned_user = db.query(User).filter(
        User.id == data.assigned_to
    ).first()

    if not assigned_user:
        raise HTTPException(
            status_code=404,
            detail="Assigned user not found"
        )

    return create_obligation(db, data)


# GET ALL OBLIGATIONS
@router.get(
    "",
    response_model=list[ObligationResponse]
)
def get_obligations_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_all_obligations(db)


# GET OBLIGATION BY ID
@router.get(
    "/{obligation_id}",
    response_model=ObligationResponse
)
def get_obligation_api(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obligation = get_obligation_by_id(
        db,
        obligation_id
    )

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail="Obligation not found"
        )

    return obligation


# UPDATE OBLIGATION
@router.put(
    "/{obligation_id}",
    response_model=ObligationResponse
)
def update_obligation_api(
    obligation_id: int,
    data: ObligationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if data.assigned_to is not None:
        user = db.query(User).filter(
            User.id == data.assigned_to
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="Assigned user not found"
            )

    obligation = update_obligation(
        db,
        obligation_id,
        data
    )

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail="Obligation not found"
        )

    return obligation


# UPDATE OBLIGATION STATUS
@router.patch(
    "/{obligation_id}/status",
    response_model=ObligationResponse
)
def update_status_api(
    obligation_id: int,
    data: ObligationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obligation, error = update_obligation_status(
        db,
        obligation_id,
        data.status
    )

    if error == "Obligation not found":
        raise HTTPException(
            status_code=404,
            detail=error
        )

    if error:
        raise HTTPException(
            status_code=400,
            detail=error
        )

    return obligation


# COMPLETE OBLIGATION
@router.post(
    "/{obligation_id}/complete",
    response_model=ObligationResponse
)
def complete_obligation_api(
    obligation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    obligation, error = complete_obligation(
        db,
        obligation_id
    )

    if error == "Obligation not found":
        raise HTTPException(
            status_code=404,
            detail=error
        )

    if error:
        raise HTTPException(
            status_code=400,
            detail=error
        )

    return obligation