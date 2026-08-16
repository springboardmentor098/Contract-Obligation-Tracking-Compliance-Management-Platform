from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.contract import ContractCreate, ContractResponse
from app.services.contract import (
    create_contract,
    get_all_contracts,
    get_contract_by_id,
)

router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)


# CREATE CONTRACT
@router.post(
    "",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED
)
def create_contract_api(
    contract_data: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return create_contract(
            db,
            contract_data,
            current_user.id
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract number already exists"
        )


# GET ALL CONTRACTS
@router.get(
    "",
    response_model=list[ContractResponse]
)
def get_contracts_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_all_contracts(db)


# GET CONTRACT BY ID
@router.get(
    "/{contract_id}",
    response_model=ContractResponse
)
def get_contract_api(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = get_contract_by_id(db, contract_id)

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return contract