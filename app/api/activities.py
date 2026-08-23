from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.activity import Activity
from app.models.contract import Contract
from app.schemas.activity_schema import ActivityCreate, ActivityRead
from app.services.audit_service import create_audit_log
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/activities",
    tags=["Activities"],
)


# =========================================================
# CREATE ACTIVITY
# =========================================================

@router.post(
    "",
    response_model=ActivityRead,
    status_code=status.HTTP_201_CREATED,
)
def create_activity(
    activity_data: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])

    # Activities are created on behalf of the authenticated user.
    # Ignore any different user_id supplied by the client.
    if activity_data.contract_id is not None:
        contract = (
            db.query(Contract)
            .filter(Contract.id == activity_data.contract_id)
            .first()
        )

        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found",
            )

    activity = Activity(
        user_id=user_id,
        contract_id=activity_data.contract_id,
        activity_type=activity_data.activity_type,
        description=activity_data.description,
    )

    db.add(activity)
    db.flush()

    create_audit_log(
        db=db,
        user_id=user_id,
        contract_id=activity.contract_id,
        action="Created activity",
        entity_type="Activity",
        entity_id=activity.id,
        details=(
            f"Created activity '{activity.activity_type}'"
        ),
    )

    db.commit()
    db.refresh(activity)

    return activity


# =========================================================
# LIST CURRENT USER ACTIVITIES
# =========================================================

@router.get(
    "",
    response_model=list[ActivityRead],
)
def list_activities(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])

    return (
        db.query(Activity)
        .filter(Activity.user_id == user_id)
        .order_by(Activity.created_at.desc())
        .all()
    )


# =========================================================
# GET CURRENT USER ACTIVITY
# =========================================================

@router.get(
    "/{activity_id}",
    response_model=ActivityRead,
)
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])

    activity = (
        db.query(Activity)
        .filter(
            Activity.id == activity_id,
            Activity.user_id == user_id,
        )
        .first()
    )

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found",
        )

    return activity
