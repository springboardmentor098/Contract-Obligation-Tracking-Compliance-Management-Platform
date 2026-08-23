from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.report import Report
from app.models.user import User
from app.models.contract import Contract
from app.schemas.report_schema import (
    ReportCreate,
    ReportUpdate,
    ReportRead,
)
from app.services.audit_service import create_audit_log
from app.core.dependencies import get_current_user, require_permission
from app.core.permissions import Permission


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


# =========================================================
# CREATE REPORT
# =========================================================

@router.post(
    "",
    response_model=ReportRead,
    status_code=status.HTTP_201_CREATED,
)
def create_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.MANAGE_USERS)
    ),
):
    user = (
        db.query(User)
        .filter(User.id == report_data.user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create report for inactive user",
        )

    if report_data.contract_id is not None:
        contract = (
            db.query(Contract)
            .filter(Contract.id == report_data.contract_id)
            .first()
        )

        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found",
            )

    report = Report(
        user_id=report_data.user_id,
        contract_id=report_data.contract_id,
        report_type=report_data.report_type,
        title=report_data.title,
        description=report_data.description,
        file_path=report_data.file_path,
    )

    db.add(report)
    db.flush()

    create_audit_log(
        db=db,
        user_id=int(current_user["sub"]),
        contract_id=report.contract_id,
        action="Created report",
        entity_type="Report",
        entity_id=report.id,
        details=(
            f"Created report '{report.title}' "
            f"for user ID {report.user_id}"
        ),
    )

    db.commit()
    db.refresh(report)

    return report


# =========================================================
# LIST CURRENT USER REPORTS
# =========================================================

@router.get(
    "",
    response_model=list[ReportRead],
)
def list_reports(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])

    return (
        db.query(Report)
        .filter(Report.user_id == user_id)
        .order_by(Report.generated_at.desc())
        .all()
    )


# =========================================================
# GET CURRENT USER REPORT
# =========================================================

@router.get(
    "/{report_id}",
    response_model=ReportRead,
)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])

    report = (
        db.query(Report)
        .filter(
            Report.id == report_id,
            Report.user_id == user_id,
        )
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    return report


# =========================================================
# UPDATE CURRENT USER REPORT
# =========================================================

@router.put(
    "/{report_id}",
    response_model=ReportRead,
)
def update_report(
    report_id: int,
    report_data: ReportUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = int(current_user["sub"])

    report = (
        db.query(Report)
        .filter(
            Report.id == report_id,
            Report.user_id == user_id,
        )
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    changes = []

    if report_data.report_type is not None:
        if report.report_type != report_data.report_type:
            changes.append(
                f"report_type: {report.report_type} -> "
                f"{report_data.report_type}"
            )
            report.report_type = report_data.report_type

    if report_data.title is not None:
        if report.title != report_data.title:
            changes.append(
                f"title: {report.title} -> "
                f"{report_data.title}"
            )
            report.title = report_data.title

    if report_data.description is not None:
        if report.description != report_data.description:
            changes.append(
                f"description: {report.description} -> "
                f"{report_data.description}"
            )
            report.description = report_data.description

    if report_data.file_path is not None:
        if report.file_path != report_data.file_path:
            changes.append(
                f"file_path: {report.file_path} -> "
                f"{report_data.file_path}"
            )
            report.file_path = report_data.file_path

    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No changes provided",
        )

    create_audit_log(
        db=db,
        user_id=user_id,
        contract_id=report.contract_id,
        action="Updated report",
        entity_type="Report",
        entity_id=report.id,
        details="; ".join(changes),
    )

    db.commit()
    db.refresh(report)

    return report


# =========================================================
# DELETE REPORT
# =========================================================

@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission(Permission.MANAGE_USERS)
    ),
):
    report = (
        db.query(Report)
        .filter(Report.id == report_id)
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )

    title = report.title
    contract_id = report.contract_id
    user_id = report.user_id

    create_audit_log(
        db=db,
        user_id=int(current_user["sub"]),
        contract_id=contract_id,
        action="Deleted report",
        entity_type="Report",
        entity_id=report.id,
        details=(
            f"Deleted report '{title}' "
            f"for user ID {user_id}"
        ),
    )

    db.delete(report)
    db.commit()

    return None
