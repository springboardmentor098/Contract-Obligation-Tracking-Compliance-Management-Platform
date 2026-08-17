from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.user import User
from app.schemas.contract import (
    ContractCreate,
    ContractResponse,
    ContractUpdate,
)
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)


@router.post(
    "/",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED
)
def create_contract(
    contract_data: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = Contract(
        owner_id=current_user.id,
        contract_code=contract_data.contract_code,
        title=contract_data.title,
        description=contract_data.description,
        counterparty=contract_data.counterparty,
        category=contract_data.category,
        status="Draft",
        risk_level=contract_data.risk_level,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date
    )

    db.add(contract)

    try:
        db.commit()
        db.refresh(contract)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contract code already exists"
        )

    return contract


@router.get(
    "/",
    response_model=list[ContractResponse]
)
def get_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contracts = (
        db.query(Contract)
        .filter(Contract.owner_id == current_user.id)
        .all()
    )

    return contracts


@router.get(
    "/{contract_id}",
    response_model=ContractResponse
)
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id,
            Contract.owner_id == current_user.id
        )
        .first()
    )

    if contract is None:
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = (
        db.query(Contract)
        .filter(
            Contract.id == contract_id,
            Contract.owner_id == current_user.id
        )
        .first()
    )

    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    update_data = contract_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(contract, field, value)

    try:
        db.commit()
        db.refresh(contract)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contract code already exists"
        )

    return contract