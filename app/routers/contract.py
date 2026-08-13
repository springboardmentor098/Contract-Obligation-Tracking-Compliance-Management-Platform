# app/routers/contract.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.schemas.contract import ContractCreate, ContractResponse
from app.dependencies.authorization import require_roles


router = APIRouter(
    prefix="/contracts",
    tags=["Contracts"]
)


# Create Contract
# Administrator, Legal Manager, Contract Manager

@router.post(
    "",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED
)
def create_contract(
    contract_data: ContractCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Contract Manager"
        )
    )
):
    contract = Contract(
        title=contract_data.title,
        contract_number=contract_data.contract_number,
        category=contract_data.category,
        description=contract_data.description,
        start_date=contract_data.start_date,
        end_date=contract_data.end_date,
        status=contract_data.status,
        owner_id=contract_data.owner_id
    )

    db.add(contract)
    db.commit()
    db.refresh(contract)
    print(
        "CREATED CONTRACT:",
        contract.id,
        contract.contract_number,
        contract.title
    )


    return contract



# Get All Contracts
# All roles

@router.get(
    "",
    response_model=list[ContractResponse]
)
def get_contracts(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Compliance Officer",
            "Contract Manager",
            "Department Head",
            "Employee"
        )
    )
):
    return db.query(Contract).all()


# Get Contract by ID
# All roles

@router.get(
    "/{contract_id}",
    response_model=ContractResponse
)
def get_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Compliance Officer",
            "Contract Manager",
            "Department Head",
            "Employee"
        )
    )
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail=f"Contract {contract_id} not found"
        )

    return contract


# Update Contract
# Administrator, Legal Manager, Contract Manager

@router.put(
    "/{contract_id}",
    response_model=ContractResponse
)
def update_contract(
    contract_id: int,
    contract_data: ContractCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Contract Manager"
        )
    )
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail=f"Contract {contract_id} not found"
        )

    contract.title = contract_data.title
    contract.contract_number = contract_data.contract_number
    contract.category = contract_data.category
    contract.description = contract_data.description
    contract.start_date = contract_data.start_date
    contract.end_date = contract_data.end_date
    contract.status = contract_data.status
    contract.owner_id = contract_data.owner_id

    db.commit()
    db.refresh(contract)

    return contract


# Delete Contract
# Administrator, Legal Manager, Contract Manager

@router.delete(
    "/{contract_id}",
    status_code=status.HTTP_200_OK
)
def delete_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_roles(
            "Administrator",
            "Legal Manager",
            "Contract Manager"
        )
    )
):
    contract = db.query(Contract).filter(
        Contract.id == contract_id
    ).first()

    if not contract:
        raise HTTPException(
            status_code=404,
            detail=f"Contract {contract_id} not found"
        )

    db.delete(contract)
    db.commit()

    return {
        "message": f"Contract {contract_id} deleted successfully"
    }