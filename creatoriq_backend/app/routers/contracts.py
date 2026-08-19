from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.schemas.contract import ContractCreate, ContractResponse
from app.models.user import User
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)


# 1. POST - Create Contract
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
    # Check if contract number already exists
    existing_contract = (
        db.query(Contract)
        .filter(
            Contract.contract_number == contract_data.contract_number
        )
        .first()
    )

    if existing_contract:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract number already exists"
        )

    contract = Contract(
        title=contract_data.title,
        contract_number=contract_data.contract_number,
        category=contract_data.category,
        description=contract_data.description,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        status="Draft",

        # Get both values from authenticated user
        created_by=current_user.id,
        assigned_to=current_user.id
    )

    db.add(contract)
    db.commit()
    db.refresh(contract)

    return contract


# 2. GET - Get All Contracts
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


# 3. GET - Get Contract by ID
@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def get_contract_by_id(
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
            detail=f"Contract with ID {contract_id} not found"
        )

    return contract