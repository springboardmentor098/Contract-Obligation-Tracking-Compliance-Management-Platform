# app/routers/renewals.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.renewal import Renewal
from app.schemas.renewal import RenewalCreate, RenewalResponse

router = APIRouter(
    prefix="/renewals",
    tags=["Renewals"]
)


@router.post(
    "",
    response_model=RenewalResponse,
    status_code=status.HTTP_201_CREATED
)
def create_renewal(
    data: RenewalCreate,
    db: Session = Depends(get_db)
):
    renewal = Renewal(**data.model_dump())

    db.add(renewal)
    db.commit()
    db.refresh(renewal)

    return renewal


@router.get("", response_model=list[RenewalResponse])
def get_renewals(db: Session = Depends(get_db)):
    return db.query(Renewal).all()


@router.get("/{renewal_id}", response_model=RenewalResponse)
def get_renewal(
    renewal_id: int,
    db: Session = Depends(get_db)
):
    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=404,
            detail=f"Renewal {renewal_id} not found"
        )

    return renewal


@router.put("/{renewal_id}", response_model=RenewalResponse)
def update_renewal(
    renewal_id: int,
    data: RenewalCreate,
    db: Session = Depends(get_db)
):
    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=404,
            detail=f"Renewal {renewal_id} not found"
        )

    for key, value in data.model_dump().items():
        setattr(renewal, key, value)

    db.commit()
    db.refresh(renewal)

    return renewal


@router.delete("/{renewal_id}")
def delete_renewal(
    renewal_id: int,
    db: Session = Depends(get_db)
):
    renewal = db.query(Renewal).filter(
        Renewal.id == renewal_id
    ).first()

    if not renewal:
        raise HTTPException(
            status_code=404,
            detail=f"Renewal {renewal_id} not found"
        )

    db.delete(renewal)
    db.commit()

    return {
        "message": f"Renewal {renewal_id} deleted successfully"
    }
