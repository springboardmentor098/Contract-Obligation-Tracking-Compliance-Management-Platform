from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.schemas.contract import ContractCreate, ContractResponse
from app.core.dependencies import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)


@router.post(
    "",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED
)
def create_contract(
    contract_data: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = Contract(
        title=contract_data.title,
        contract_number=contract_data.contract_number,
        category=contract_data.category,
        description=contract_data.description,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        status="Draft",
        created_by=current_user.id
    )

    db.add(contract)

    try:
        db.commit()
        db.refresh(contract)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contract number already exists"
        )

    return contract


@router.get(
    "",
    response_model=list[ContractResponse],
    status_code=status.HTTP_200_OK
)
def get_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Contract).all()


@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return contract