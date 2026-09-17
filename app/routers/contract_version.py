# app/routers/contract_versions.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.contract_version import ContractVersion
from app.schemas.contract_version import (
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
    data: ContractVersionCreate,
    db: Session = Depends(get_db)
):
    version = ContractVersion(**data.model_dump())

    db.add(version)
    db.commit()
    db.refresh(version)

    return version


@router.get(
    "",
    response_model=list[ContractVersionResponse]
)
def get_contract_versions(
    db: Session = Depends(get_db)
):
    return db.query(ContractVersion).all()


@router.get(
    "/{version_id}",
    response_model=ContractVersionResponse
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
            status_code=404,
            detail=f"Contract Version {version_id} not found"
        )

    return version


@router.put(
    "/{version_id}",
    response_model=ContractVersionResponse
)
def update_contract_version(
    version_id: int,
    data: ContractVersionCreate,
    db: Session = Depends(get_db)
):
    version = db.query(ContractVersion).filter(
        ContractVersion.id == version_id
    ).first()

    if not version:
        raise HTTPException(
            status_code=404,
            detail=f"Contract Version {version_id} not found"
        )

    for key, value in data.model_dump().items():
        setattr(version, key, value)

    db.commit()
    db.refresh(version)

    return version


@router.delete("/{version_id}")
def delete_contract_version(
    version_id: int,
    db: Session = Depends(get_db)
):
    version = db.query(ContractVersion).filter(
        ContractVersion.id == version_id
    ).first()

    if not version:
        raise HTTPException(
            status_code=404,
            detail=f"Contract Version {version_id} not found"
        )

    db.delete(version)
    db.commit()

    return {
        "message": f"Contract Version {version_id} deleted successfully"
    }
