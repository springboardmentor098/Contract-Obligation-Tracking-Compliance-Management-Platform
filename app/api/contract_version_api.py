from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract_version import ContractVersion
from app.schemas.contract_version_schema import (
    ContractVersionCreate,
    ContractVersionResponse
)


router = APIRouter(
    prefix="/contract-versions",
    tags=["Contract Versions"]
)


@router.post(
    "",
    response_model=ContractVersionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_contract_version(
    version_data: ContractVersionCreate,
    db: Session = Depends(get_db)
):
    version = ContractVersion(
        contract_id=version_data.contract_id,
        version_number=version_data.version_number,
        file_path=version_data.file_path,
        uploaded_by=version_data.uploaded_by
    )

    db.add(version)
    db.commit()
    db.refresh(version)

    return version


@router.get(
    "/",
    response_model=list[ContractVersionResponse],
    status_code=status.HTTP_200_OK
)
def get_contract_versions(
    db: Session = Depends(get_db)
):
    versions = db.query(ContractVersion).all()
    return versions


@router.get(
    "/{version_id}",
    response_model=ContractVersionResponse,
    status_code=status.HTTP_200_OK
)
def get_contract_version(
    version_id: int,
    db: Session = Depends(get_db)
):
    version = db.query(ContractVersion).filter(
        ContractVersion.id == version_id
    ).first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract version not found"
        )

    return version