from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.renewal import (
    RenewalCreate,
    RenewalUpdate,
    RenewalStatusUpdate,
    RenewalResponse,
)

from app.services.renewal import (
    create_renewal,
    get_all_renewals,
    get_renewal_by_id,
    get_contract_renewals,
    update_renewal,
    update_renewal_status,
    complete_renewal,
    get_upcoming_renewals,
    get_expired_renewals,
)


router = APIRouter(
    prefix="/renewals",
    tags=["Renewals"]
)


# CREATE RENEWAL
@router.post(
    "",
    response_model=RenewalResponse,
    status_code=status.HTTP_201_CREATED
)
def create_renewal_api(
    renewal_data: RenewalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_renewal(db, renewal_data)


# GET ALL RENEWALS
@router.get(
    "",
    response_model=list[RenewalResponse]
)
def get_renewals_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_all_renewals(db)


# GET RENEWAL BY ID
@router.get(
    "/{renewal_id}",
    response_model=RenewalResponse
)
def get_renewal_api(
    renewal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_renewal_by_id(db, renewal_id)


# GET RENEWALS FOR CONTRACT
@router.get(
    "/contract/{contract_id}",
    response_model=list[RenewalResponse]
)
def get_contract_renewals_api(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_contract_renewals(db, contract_id)


# UPDATE RENEWAL
@router.put(
    "/{renewal_id}",
    response_model=RenewalResponse
)
def update_renewal_api(
    renewal_id: int,
    renewal_data: RenewalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_renewal(
        db,
        renewal_id,
        renewal_data
    )


# UPDATE RENEWAL STATUS
@router.patch(
    "/{renewal_id}/status",
    response_model=RenewalResponse
)
def update_renewal_status_api(
    renewal_id: int,
    status_data: RenewalStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_renewal_status(
        db,
        renewal_id,
        status_data.status
    )


# COMPLETE RENEWAL
@router.post(
    "/{renewal_id}/renew",
    response_model=RenewalResponse
)
def complete_renewal_api(
    renewal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return complete_renewal(
        db,
        renewal_id
    )


# UPCOMING RENEWALS
@router.get(
    "/monitor/upcoming",
    response_model=list[RenewalResponse]
)
def upcoming_renewals_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_upcoming_renewals(db)


# EXPIRED RENEWALS
@router.get(
    "/monitor/expired",
    response_model=list[RenewalResponse]
)
def expired_renewals_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_expired_renewals(db)
