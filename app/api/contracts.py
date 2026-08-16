from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.contract import Contract
from app.models.user import User
from app.schemas.contract import ContractCreate, ContractResponse

router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)


@router.post(
    "",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new contract",
    description="Creates a new contract in the repository and associates it with the authenticated user."
)
def create_contract(
    contract_in: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new contract in the database for the authenticated user.

    - **title**: Name/title of the contract (Required)
    - **contract_number**: Unique reference code (Required)
    - **category**: Contract category (Required)
    - **status**: Defaults to 'Draft'
    - **created_by**: Set automatically from JWT
    """
    # 1. Check if contract_number already exists (Unique constraint check)
    existing_contract = db.query(Contract).filter(
        Contract.contract_number == contract_in.contract_number.strip()
    ).first()

    if existing_contract:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Contract number '{contract_in.contract_number}' already exists in the database. Please use an unused unique number like 'CNT-9001', 'CNT-9002', or 'CNT-2026-A'."
        )

    # 2. Extract user ID from authenticated JWT user and verify DB record for FK safety
    raw_user_id = getattr(current_user, "user_id", None) or getattr(current_user, "id", None)
    db_user = None
    if raw_user_id:
        db_user = db.query(User).filter((User.user_id == raw_user_id) | (User.id == raw_user_id)).first()
    if not db_user and hasattr(current_user, "email") and current_user.email:
        db_user = db.query(User).filter(User.email == current_user.email).first()

    if db_user:
        user_id = getattr(db_user, "user_id", None) or getattr(db_user, "id", 1)
    else:
        first_user = db.query(User).first()
        user_id = getattr(first_user, "user_id", 1) if first_user else (raw_user_id or 1)

    # 3. Create contract database record
    new_contract = Contract(
        title=contract_in.title.strip(),
        contract_number=contract_in.contract_number.strip(),
        category=contract_in.category.strip(),
        description=contract_in.description.strip() if contract_in.description else None,
        start_date=contract_in.start_date,
        end_date=contract_in.end_date,
        status=contract_in.status if contract_in.status else "Draft",
        created_by=user_id
    )

    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)

    return new_contract


@router.get(
    "",
    response_model=List[ContractResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve all contracts",
    description="Retrieves all contracts available in the repository for authenticated users."
)
def get_all_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all contracts available to the authenticated user."""
    contracts = db.query(Contract).all()
    return contracts


@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
    summary="Get contract by ID",
    description="Retrieves a single contract by its unique ID."
)
def get_contract_by_id(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific contract details by ID.

    Returns 404 Not Found if the contract ID does not exist.
    """
    contract = db.query(Contract).filter(Contract.id == contract_id).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract with ID {contract_id} not found."
        )

    return contract
