from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.report import Report
from app.schemas.report_schema import ReportCreate, ReportResponse


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
    report_data: ReportCreate,
    db: Session = Depends(get_db)
):
    report = Report(
        generated_by=report_data.generated_by,
        report_name=report_data.report_name,
        report_type=report_data.report_type,
        file_path=report_data.file_path
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


@router.get(
    "/",
    response_model=list[ReportResponse]
)
def get_reports(
    db: Session = Depends(get_db)
):
    return db.query(Report).all()


@router.get(
    "/{report_id}",
    response_model=ReportResponse
)
def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    report = db.query(Report).filter(
        Report.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    return report