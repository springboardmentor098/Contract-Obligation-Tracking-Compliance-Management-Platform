from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract import Contract
from app.models.contract_version import ContractVersion
from app.schemas.contract_version_schema import (
    ContractVersionCreate,
    ContractVersionRead,
)
from app.services.audit_service import create_audit_log
from app.core.dependencies import require_permission
from app.core.permissions import Permission


router = APIRouter(
    prefix="/contracts",
    tags=["Contract Versions"],
)


# =========================================================
# CREATE CONTRACT VERSION
# =========================================================

@router.post(
    "/{contract_id}/versions",
    response_model=ContractVersionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_contract_version(
    contract_id: int,
    version_data: ContractVersionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.UPDATE_CONTRACT)
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

    existing_version = (
        db.query(ContractVersion)
        .filter(
            ContractVersion.contract_id == contract_id,
            ContractVersion.version_number
            == version_data.version_number,
        )
        .first()
    )

    if existing_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Version number already exists for this contract",
        )

    version = ContractVersion(
        contract_id=contract_id,
        version_number=version_data.version_number,
        file_name=version_data.file_name,
        file_path=version_data.file_path,
        content_hash=version_data.content_hash,
        notes=version_data.notes,
    )

    db.add(version)
    db.flush()

    create_audit_log(
        db=db,
        user_id=int(current_user["sub"]),
        contract_id=contract_id,
        action="Created contract version",
        entity_type="ContractVersion",
        entity_id=version.id,
        details=(
            f"Created version '{version.version_number}' "
            f"for contract '{contract.contract_number}'"
        ),
    )

    db.commit()
    db.refresh(version)

    return version


# =========================================================
# LIST CONTRACT VERSIONS
# =========================================================

@router.get(
    "/{contract_id}/versions",
    response_model=list[ContractVersionRead],
)
def list_contract_versions(
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
        db.query(ContractVersion)
        .filter(ContractVersion.contract_id == contract_id)
        .order_by(ContractVersion.id)
        .all()
    )


# =========================================================
# GET CONTRACT VERSION
# =========================================================

@router.get(
    "/versions/{version_id}",
    response_model=ContractVersionRead,
)
def get_contract_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.READ_CONTRACT)
    ),
):
    version = (
        db.query(ContractVersion)
        .filter(ContractVersion.id == version_id)
        .first()
    )

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract version not found",
        )

    return version


# =========================================================
# DELETE CONTRACT VERSION
# =========================================================

@router.delete(
    "/versions/{version_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_contract_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.UPDATE_CONTRACT)
    ),
):
    version = (
        db.query(ContractVersion)
        .filter(ContractVersion.id == version_id)
        .first()
    )

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract version not found",
        )

    contract_id = version.contract_id
    version_number = version.version_number

    create_audit_log(
        db=db,
        user_id=int(current_user["sub"]),
        contract_id=contract_id,
        action="Deleted contract version",
        entity_type="ContractVersion",
        entity_id=version.id,
        details=(
            f"Deleted version '{version_number}' "
            f"from contract ID {contract_id}"
        ),
    )

    db.delete(version)
    db.commit()

    return None
