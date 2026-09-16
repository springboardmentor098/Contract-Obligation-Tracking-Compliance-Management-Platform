from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.renewal import Renewal
from app.schemas.renewal_schema import (
    RenewalCreate,
    RenewalUpdate,
    RenewalRead,
)
from app.services.audit_service import create_audit_log
from app.core.dependencies import require_permission
from app.core.permissions import Permission


router = APIRouter(
    prefix="/contracts",
    tags=["Renewals"],
)


# =========================================================
# CREATE RENEWAL
# =========================================================

@router.post(
    "/{contract_id}/renewals",
    response_model=RenewalRead,
    status_code=status.HTTP_201_CREATED,
)
def create_renewal(
    contract_id: int,
    renewal_data: RenewalCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.CREATE_CONTRACT)
    ),
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    renewal = Renewal(
        contract_id=contract_id,
        renewal_date=renewal_data.renewal_date,
        status=renewal_data.status,
        renewal_terms=renewal_data.renewal_terms,
    )

    db.add(renewal)
    db.flush()

    create_audit_log(
        db=db,
        user_id=int(current_user["sub"]),
        contract_id=contract_id,
        action="Created renewal",
        entity_type="Renewal",
        entity_id=renewal.id,
        details=(
            f"Created renewal for contract "
            f"'{contract.contract_number}' "
            f"on {renewal.renewal_date}"
        ),
    )

    db.commit()
    db.refresh(renewal)

    return renewal


# =========================================================
# LIST CONTRACT RENEWALS
# =========================================================

@router.get(
    "/{contract_id}/renewals",
    response_model=list[RenewalRead],
)
def list_contract_renewals(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.READ_CONTRACT)
    ),
):
    contract = (
        db.query(Contract)
        .filter(Contract.id == contract_id)
        .first()
    )

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    return (
        db.query(Renewal)
        .filter(Renewal.contract_id == contract_id)
        .order_by(Renewal.renewal_date)
        .all()
    )


# =========================================================
# GET RENEWAL
# =========================================================

@router.get(
    "/renewals/{renewal_id}",
    response_model=RenewalRead,
)
def get_renewal(
    renewal_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.READ_CONTRACT)
    ),
):
    renewal = (
        db.query(Renewal)
        .filter(Renewal.id == renewal_id)
        .first()
    )

    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found",
        )

    return renewal


# =========================================================
# UPDATE RENEWAL
# =========================================================

@router.put(
    "/renewals/{renewal_id}",
    response_model=RenewalRead,
)
def update_renewal(
    renewal_id: int,
    renewal_data: RenewalUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.UPDATE_CONTRACT)
    ),
):
    renewal = (
        db.query(Renewal)
        .filter(Renewal.id == renewal_id)
        .first()
    )

    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found",
        )

    update_data = renewal_data.model_dump(
        exclude_unset=True
    )

    old_values = []

    for field, value in update_data.items():
        old_value = getattr(renewal, field)

        if old_value != value:
            old_values.append(
                f"{field}: {old_value} -> {value}"
            )

        setattr(renewal, field, value)

    create_audit_log(
        db=db,
        user_id=int(current_user["sub"]),
        contract_id=renewal.contract_id,
        action="Updated renewal",
        entity_type="Renewal",
        entity_id=renewal.id,
        details="; ".join(old_values) or "No values changed",
    )

    db.commit()
    db.refresh(renewal)

    return renewal


# =========================================================
# DELETE RENEWAL
# =========================================================

@router.delete(
    "/renewals/{renewal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_renewal(
    renewal_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.DELETE_CONTRACT)
    ),
):
    renewal = (
        db.query(Renewal)
        .filter(Renewal.id == renewal_id)
        .first()
    )

    if not renewal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renewal not found",
        )

    contract_id = renewal.contract_id
    renewal_date = renewal.renewal_date

    create_audit_log(
        db=db,
        user_id=int(current_user["sub"]),
        contract_id=contract_id,
        action="Deleted renewal",
        entity_type="Renewal",
        entity_id=renewal.id,
        details=(
            f"Deleted renewal scheduled for {renewal_date} "
            f"from contract ID {contract_id}"
        ),
    )

    db.delete(renewal)
    db.commit()

    return None
