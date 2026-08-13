# app/routers/reports.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportResponse

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.post(
    "",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED
)
def create_report(
    data: ReportCreate,
    db: Session = Depends(get_db)
):
    report = Report(**data.model_dump())

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


@router.get("", response_model=list[ReportResponse])
def get_reports(db: Session = Depends(get_db)):
    return db.query(Report).all()


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(
        Report.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"Report {report_id} not found"
        )

    return report


@router.put("/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: int,
    data: ReportCreate,
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(
        Report.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"Report {report_id} not found"
        )

    for key, value in data.model_dump().items():
        setattr(report, key, value)

    db.commit()
    db.refresh(report)

    return report


@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(
        Report.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"Report {report_id} not found"
        )

    db.delete(report)
    db.commit()

    return {
        "message": f"Report {report_id} deleted successfully"
    }