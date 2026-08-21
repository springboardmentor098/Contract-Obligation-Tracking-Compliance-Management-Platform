from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.contract import (
    ContractCreate,
    ContractResponse,
    ContractUpdate,
    ContractStatusUpdate,
    ContractAssignment,
)
from app.services.contract import (
    create_contract,
    get_all_contracts,
    get_contract_by_id,
    update_contract,
    update_contract_status,
    submit_for_review,
    approve_contract,
    activate_contract,
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


# UPDATE CONTRACT
@router.put(
    "/{contract_id}",
    response_model=ContractResponse
)
def update_contract_api(
    contract_id: int,
    contract_data: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract = update_contract(
        db,
        contract_id,
        contract_data
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )

    return contract


# UPDATE CONTRACT STATUS
@router.patch(
    "/{contract_id}/status",
    response_model=ContractResponse
)
def update_contract_status_api(
    contract_id: int,
    status_data: ContractStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract, error = update_contract_status(
        db,
        contract_id,
        status_data.status
    )

    if error == "Contract not found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return contract


# SUBMIT CONTRACT FOR REVIEW
@router.post(
    "/{contract_id}/submit-review",
    response_model=ContractResponse
)
def submit_contract_for_review_api(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract, error = submit_for_review(
        db,
        contract_id
    )

    if error == "Contract not found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return contract


# APPROVE CONTRACT
@router.post(
    "/{contract_id}/approve",
    response_model=ContractResponse
)
def approve_contract_api(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only authorized roles can approve contracts
    allowed_roles = [
        "Administrator",
        "Legal Manager"
    ]

    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to approve contracts"
        )

    contract, error = approve_contract(
        db,
        contract_id
    )

    if error == "Contract not found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return contract


# ACTIVATE CONTRACT
@router.post(
    "/{contract_id}/activate",
    response_model=ContractResponse
)
def activate_contract_api(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contract, error = activate_contract(
        db,
        contract_id
    )

    if error == "Contract not found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error
        )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    return contract
