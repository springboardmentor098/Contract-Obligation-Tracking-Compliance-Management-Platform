from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.schemas.contract_schema import ContractCreate, ContractResponse
from app.middleware.auth import require_roles


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)


# ============================================================
# CREATE CONTRACT
# Administrator, Legal Manager, Contract Manager
# ============================================================

@router.post(
    "",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            require_roles(
                "Administrator",
                "Legal Manager",
                "Contract Manager"
            )
        )
    ]
)
def create_contract(
    contract_data: ContractCreate,
    db: Session = Depends(get_db)
):

    # Check duplicate contract number
    if contract_data.contract_number:
        existing_contract = db.query(Contract).filter(
            Contract.contract_number == contract_data.contract_number
        ).first()

        if existing_contract:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Contract number already exists"
            )

    # Check owner exists
    from app.models.user import User

    owner = db.query(User).filter(
        User.id == contract_data.owner_id
    ).first()

    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract owner not found"
        )

    contract = Contract(
        title=contract_data.title,
        contract_number=contract_data.contract_number,
        description=contract_data.description,
        party_name=contract_data.party_name,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        status=contract_data.status,
        owner_id=contract_data.owner_id
    )

    db.add(contract)
    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# GET ALL CONTRACTS
# All authenticated roles can view contracts
# ============================================================

@router.get(
    "",
    response_model=list[ContractResponse],
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            require_roles(
                "Administrator",
                "Legal Manager",
                "Compliance Officer",
                "Contract Manager",
                "Department Head",
                "Employee"
            )
        )
    ]
)
def get_contracts(
    db: Session = Depends(get_db)
):

    contracts = db.query(Contract).all()

    return contracts


# ============================================================
# GET CONTRACT BY ID
# All authenticated roles can view contracts
# ============================================================

@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            require_roles(
                "Administrator",
                "Legal Manager",
                "Compliance Officer",
                "Contract Manager",
                "Department Head",
                "Employee"
            )
        )
    ]
)
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db)
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


# ============================================================
# UPDATE CONTRACT
# Administrator, Legal Manager, Contract Manager
# ============================================================

@router.put(
    "/{contract_id}",
    response_model=ContractResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            require_roles(
                "Administrator",
                "Legal Manager",
                "Contract Manager"
            )
        )
    ]
)
def update_contract(
    contract_id: int,
    contract_data: ContractCreate,
    db: Session = Depends(get_db)
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    # Check duplicate contract number
    if contract_data.contract_number:

        existing_contract = db.query(Contract).filter(
            Contract.contract_number == contract_data.contract_number,
            Contract.id != contract_id
        ).first()

        if existing_contract:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Contract number already exists"
            )

    # Check owner
    from app.models.user import User

    owner = db.query(User).filter(
        User.id == contract_data.owner_id
    ).first()

    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract owner not found"
        )

    contract.title = contract_data.title
    contract.contract_number = contract_data.contract_number
    contract.description = contract_data.description
    contract.party_name = contract_data.party_name
    contract.start_date = contract_data.start_date
    contract.end_date = contract_data.end_date
    contract.status = contract_data.status
    contract.owner_id = contract_data.owner_id

    db.commit()
    db.refresh(contract)

    return contract


# ============================================================
# DELETE CONTRACT
# Administrator, Contract Manager
# ============================================================

@router.delete(
    "/{contract_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            require_roles(
                "Administrator",
                "Contract Manager"
            )
        )
    ]
)
def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db)
):

    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    db.delete(contract)
    db.commit()

    return {
        "message": "Contract deleted successfully"
    }