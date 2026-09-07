# app/routers/activities.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate, ActivityResponse

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
    data: ActivityCreate,
    db: Session = Depends(get_db)
):
    activity = Activity(**data.model_dump())

    db.add(activity)
    db.commit()
    db.refresh(activity)

    return activity


@router.get("", response_model=list[ActivityResponse])
def get_activities(db: Session = Depends(get_db)):
    return db.query(Activity).all()


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db)
):
    activity = db.query(Activity).filter(
        Activity.id == activity_id
    ).first()

    if not activity:
        raise HTTPException(
            status_code=404,
            detail=f"Activity {activity_id} not found"
        )

    return activity


@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    data: ActivityCreate,
    db: Session = Depends(get_db)
):
    activity = db.query(Activity).filter(
        Activity.id == activity_id
    ).first()

    if not activity:
        raise HTTPException(
            status_code=404,
            detail=f"Activity {activity_id} not found"
        )

    for key, value in data.model_dump().items():
        setattr(activity, key, value)

    db.commit()
    db.refresh(activity)

    return activity


@router.delete("/{activity_id}")
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db)
):
    activity = db.query(Activity).filter(
        Activity.id == activity_id
    ).first()

    if not activity:
        raise HTTPException(
            status_code=404,
            detail=f"Activity {activity_id} not found"
        )

    db.delete(activity)
    db.commit()

    return {
        "message": f"Activity {activity_id} deleted successfully"
    }