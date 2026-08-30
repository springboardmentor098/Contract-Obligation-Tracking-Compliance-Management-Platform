from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.database import get_db
from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.user import User
from app.schemas.obligation import (
    ObligationCreate,
    ObligationResponse,
    ObligationStatusUpdate,
    ObligationUpdate,
)
from app.services.compliance_service import (
    get_upcoming_obligations as get_upcoming_obligations_service,
)

router = APIRouter(
    prefix="/obligations",
    tags=["Obligations"],
)


def get_obligation_or_404(
    obligation_id: UUID,
    db: Session,
) -> Obligation:
    obligation = db.get(Obligation, obligation_id)

    if not obligation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Obligation not found",
        )

    return obligation


def get_contract_or_404(
    contract_id: UUID,
    db: Session,
) -> Contract:
    contract = db.get(Contract, contract_id)

    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found",
        )

    return contract


def get_user_or_404(
    user_id: UUID,
    db: Session,
) -> User:
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assigned user is inactive",
        )

    return user


def check_contract_access(
    contract: Contract,
    current_user: User,
) -> None:
    if current_user.role.lower() == "admin":
        return

    if contract.created_by == current_user.id:
        return

    if contract.assigned_to == current_user.id:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this contract",
    )


def check_obligation_access(
    obligation: Obligation,
    contract: Contract,
    current_user: User,
) -> None:
    if current_user.role.lower() == "admin":
        return

    if contract.created_by == current_user.id:
        return

    if contract.assigned_to == current_user.id:
        return

    if obligation.assigned_to == current_user.id:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to access this obligation",
    )


@router.post(
    "",
    response_model=ObligationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_obligation(
    data: ObligationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contract = get_contract_or_404(data.contract_id, db)
    check_contract_access(contract, current_user)

    get_user_or_404(data.assigned_to, db)

    obligation = Obligation(
        contract_id=data.contract_id,
        assigned_to=data.assigned_to,
        title=data.title,
        description=data.description,
        obligation_type=data.obligation_type,
        due_date=data.due_date,
        status=data.status or "Pending",
        priority=data.priority or "Medium",
    )

    db.add(obligation)
    db.commit()
    db.refresh(obligation)

    return obligation


@router.get(
    "",
    response_model=list[ObligationResponse],
)
def get_all_obligations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role.lower() == "admin":
        return db.execute(
            select(Obligation)
        ).scalars().all()

    return db.execute(
        select(Obligation)
        .join(
            Contract,
            Obligation.contract_id == Contract.id,
        )
        .where(
            (Contract.created_by == current_user.id)
            | (Contract.assigned_to == current_user.id)
            | (Obligation.assigned_to == current_user.id)
        )
    ).scalars().all()


@router.get(
    "/{obligation_id}",
    response_model=ObligationResponse,
)
def get_obligation(
    obligation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obligation = get_obligation_or_404(obligation_id, db)

    contract = get_contract_or_404(obligation.contract_id, db)
    check_obligation_access(obligation, contract, current_user)

    return obligation


@router.put(
    "/{obligation_id}",
    response_model=ObligationResponse,
)
def update_obligation(
    obligation_id: UUID,
    data: ObligationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obligation = get_obligation_or_404(obligation_id, db)

    contract = get_contract_or_404(obligation.contract_id, db)
    check_obligation_access(obligation, contract, current_user)

    if data.assigned_to is not None:
        get_user_or_404(data.assigned_to, db)

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(obligation, field, value)

    db.commit()
    db.refresh(obligation)

    return obligation


@router.patch(
    "/{obligation_id}/status",
    response_model=ObligationResponse,
)
def update_obligation_status(
    obligation_id: UUID,
    data: ObligationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obligation = get_obligation_or_404(obligation_id, db)

    contract = get_contract_or_404(obligation.contract_id, db)
    check_obligation_access(obligation, contract, current_user)

    obligation.status = data.status

    if data.status.lower() == "completed":
        obligation.completed_at = datetime.utcnow()
    else:
        obligation.completed_at = None

    db.commit()
    db.refresh(obligation)

    return obligation


@router.delete(
    "/{obligation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_obligation(
    obligation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obligation = get_obligation_or_404(obligation_id, db)

    contract = get_contract_or_404(obligation.contract_id, db)
    check_obligation_access(obligation, contract, current_user)

    db.delete(obligation)
    db.commit()

    return None


@router.get(
    "/upcoming/list",
    response_model=list[ObligationResponse],
)
def get_upcoming_obligations(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obligations = get_upcoming_obligations_service(
        db=db,
        days=days,
    )

    if current_user.role.lower() == "admin":
        return obligations

    return [
        obligation
        for obligation in obligations
        if (
            obligation.assigned_to == current_user.id
            or (
                obligation.contract
                and (
                    obligation.contract.created_by == current_user.id
                    or obligation.contract.assigned_to == current_user.id
                )
            )
        )
    ]