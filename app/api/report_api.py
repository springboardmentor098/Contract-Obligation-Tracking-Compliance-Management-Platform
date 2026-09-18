from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.role_checker import RoleChecker
from app.database.database import get_db
from app.models.report import Report
from app.schemas.report_schema import ReportCreate, ReportResponse
from app.services.activity_service import log_activity
from app.services.report_service import (
    gather_report_data,
    generate_pdf_report,
    get_or_render_report_file,
    sanitize_filename,
    save_report_file,
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    dependencies=[Depends(RoleChecker(["Admin", "Legal Manager", "Compliance Officer", "Viewer"]))],
)


@router.post(
    "",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_report(
    report_data: ReportCreate,
    request: Request,
    current_user=Depends(RoleChecker(["Admin", "Legal Manager", "Compliance Officer"])),
    db: Session = Depends(get_db),
):
    # 1. Gather live PostgreSQL data
    data = gather_report_data(db, report_data.report_type, current_user)

    # 2. Pre-generate and store primary PDF file
    clean_name = sanitize_filename(report_data.report_name)
    filename = f"{clean_name}_{uuid4().hex[:8]}.pdf"
    pdf_bytes = generate_pdf_report(data)

    try:
        stored_path = save_report_file(pdf_bytes, filename)
    except Exception:
        stored_path = f"uploads/reports/{filename}"

    # 3. Store record in reports table
    report = Report(
        generated_by=current_user.id,
        report_name=report_data.report_name,
        report_type=report_data.report_type,
        file_path=stored_path,
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    # Automatically record GENERATE_REPORT activity log
    log_activity(
        db=db,
        action="GENERATE_REPORT",
        entity_type="Report",
        entity_id=report.id,
        contract_id=None,
        description=f"Generated {report.report_type} '{report.report_name}'",
        user=current_user,
        request=request,
    )

    return report


@router.get(
    "",
    response_model=list[ReportResponse],
)
@router.get(
    "/",
    response_model=list[ReportResponse],
    include_in_schema=False,
)
def get_reports(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Report).order_by(Report.id.desc()).all()


@router.get(
    "/{report_id}/download",
)
def download_report(
    report_id: int,
    request: Request,
    format: str = Query("pdf", description="Download format: pdf or csv"),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    requested_format = format.lower().strip()
    if requested_format not in ["pdf", "csv"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format. Only 'pdf' and 'csv' are supported.",
        )

    content, filename, media_type = get_or_render_report_file(
        report=report,
        format_type=requested_format,
        db=db,
    )

    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Access-Control-Expose-Headers": "Content-Disposition",
    }

    # Automatically record DOWNLOAD_REPORT activity log
    log_activity(
        db=db,
        action="DOWNLOAD_REPORT",
        entity_type="Report",
        entity_id=report.id,
        contract_id=None,
        description=f"Downloaded report '{report.report_name}' ({requested_format.upper()})",
        user=current_user,
        request=request,
    )

    return Response(
        content=content,
        media_type=media_type,
        headers=headers,
    )


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
)
def get_report(
    report_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    return report


@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_report(
    report_id: int,
    request: Request,
    current_user=Depends(RoleChecker(["Admin", "Legal Manager"])),
    db: Session = Depends(get_db),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    report_name = report.report_name
    db.delete(report)
    db.commit()

    log_activity(
        db=db,
        action="DELETE_REPORT",
        entity_type="Report",
        entity_id=report_id,
        contract_id=None,
        description=f"Deleted report '{report_name}'",
        user=current_user,
        request=request,
    )

    return None
