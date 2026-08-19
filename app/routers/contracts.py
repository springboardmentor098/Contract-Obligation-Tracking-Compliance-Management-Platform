from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.schemas.contract import ContractCreate, ContractResponse
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)


# =========================
# CREATE CONTRACT
# =========================

@router.post(
    "",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED
)
def create_contract(
    contract_data: ContractCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Check duplicate contract number
    existing_contract = db.query(Contract).filter(
        Contract.contract_number == contract_data.contract_number
    ).first()

    if existing_contract:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract number already exists"
        )

    contract = Contract(
        contract_number=contract_data.contract_number,
        title=contract_data.title,
        category=contract_data.category,
        description=contract_data.description,
        party_name=contract_data.party_name,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        status="Draft",
        owner_id=current_user["user_id"]
    )

    try:
        db.add(contract)
        db.commit()
        db.refresh(contract)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract number already exists"
        )

    return contract


# =========================
# GET ALL CONTRACTS
# =========================

@router.get(
    "",
    response_model=list[ContractResponse],
    status_code=status.HTTP_200_OK
)
def get_contracts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    contracts = db.query(Contract).all()

    return contracts


# =========================
# GET CONTRACT BY ID
# =========================

@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK
)
def get_contract(
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

    return contract 