# app/routers/obligations.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.obligation import Obligation
from app.schemas.obligation import ObligationCreate, ObligationResponse

router = APIRouter(
    prefix="/obligations",
    tags=["Obligations"]
)


@router.post(
    "",
    response_model=ObligationResponse,
    status_code=status.HTTP_201_CREATED
)
def create_obligation(
    data: ObligationCreate,
    db: Session = Depends(get_db)
):
    obligation = Obligation(**data.model_dump())

    db.add(obligation)
    db.commit()
    db.refresh(obligation)

    return obligation


@router.get("", response_model=list[ObligationResponse])
def get_obligations(db: Session = Depends(get_db)):
    return db.query(Obligation).all()


@router.get("/{obligation_id}", response_model=ObligationResponse)
def get_obligation(
    obligation_id: int,
    db: Session = Depends(get_db)
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail=f"Obligation {obligation_id} not found"
        )

    return obligation


@router.put("/{obligation_id}", response_model=ObligationResponse)
def update_obligation(
    obligation_id: int,
    data: ObligationCreate,
    db: Session = Depends(get_db)
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail=f"Obligation {obligation_id} not found"
        )

    for key, value in data.model_dump().items():
        setattr(obligation, key, value)

    db.commit()
    db.refresh(obligation)

    return obligation


@router.delete("/{obligation_id}")
def delete_obligation(
    obligation_id: int,
    db: Session = Depends(get_db)
):
    obligation = db.query(Obligation).filter(
        Obligation.id == obligation_id
    ).first()

    if not obligation:
        raise HTTPException(
            status_code=404,
            detail=f"Obligation {obligation_id} not found"
        )

    db.delete(obligation)
    db.commit()

    return {
        "message": f"Obligation {obligation_id} deleted successfully"
    }
