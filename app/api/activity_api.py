from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.activity import Activity
from app.schemas.activity_schema import ActivityCreate, ActivityResponse


router = APIRouter(
    prefix="/activities",
    tags=["Activities"]
)


@router.post(
    "",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED
)
def create_activity(
    activity_data: ActivityCreate,
    db: Session = Depends(get_db)
):
    activity = Activity(
        user_id=activity_data.user_id,
        contract_id=activity_data.contract_id,
        activity=activity_data.activity
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    return activity


@router.get(
    "/",
    response_model=list[ActivityResponse]
)
def get_activities(
    db: Session = Depends(get_db)
):
    return db.query(Activity).all()


@router.get(
    "/{activity_id}",
    response_model=ActivityResponse
)
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db)
):
    activity = db.query(Activity).filter(
        Activity.id == activity_id
    ).first()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    return activity