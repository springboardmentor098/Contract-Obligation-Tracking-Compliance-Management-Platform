from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportResponse

from app.services.report_service import (
    get_dashboard_summary,
    get_contract_summary,
    get_obligation_summary,
    get_renewal_summary,
    get_compliance_summary,
    get_risk_analysis,
    get_contract_report,
    get_obligation_report,
    get_renewal_report,
    get_compliance_report,
    get_department_performance,
    generate_contract_pdf,
    generate_obligation_pdf,
    generate_renewal_pdf,
    generate_compliance_pdf,
    generate_contract_excel,
    generate_obligation_excel,
    generate_renewal_excel,
    generate_compliance_excel,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


# =========================================================
# DASHBOARD / ANALYTICS
# =========================================================

@router.get("/dashboard/summary")
def dashboard_summary(
    db: Session = Depends(get_db)
):
    return get_dashboard_summary(db)


@router.get("/contracts/summary")
def contract_summary(
    db: Session = Depends(get_db)
):
    return get_contract_summary(db)


@router.get("/obligations/summary")
def obligation_summary(
    db: Session = Depends(get_db)
):
    return get_obligation_summary(db)


@router.get("/renewals/summary")
def renewal_summary(
    db: Session = Depends(get_db)
):
    return get_renewal_summary(db)


@router.get("/compliance/summary")
def compliance_summary(
    db: Session = Depends(get_db)
):
    return get_compliance_summary(db)


@router.get("/risk")
def risk_analysis(
    db: Session = Depends(get_db)
):
    return get_risk_analysis(db)


@router.get("/departments/performance")
def department_performance(
    db: Session = Depends(get_db)
):
    return get_department_performance(db)


# =========================================================
# REPORT DATA
# =========================================================

@router.get("/contracts/report")
def contract_report(
    db: Session = Depends(get_db)
):
    return get_contract_report(db)


@router.get("/obligations/report")
def obligation_report(
    db: Session = Depends(get_db)
):
    return get_obligation_report(db)


@router.get("/renewals/report")
def renewal_report(
    db: Session = Depends(get_db)
):
    return get_renewal_report(db)


@router.get("/compliance/report")
def compliance_report(
    db: Session = Depends(get_db)
):
    return get_compliance_report(db)


# =========================================================
# PDF REPORTS
# =========================================================

@router.get("/contracts/pdf")
def contract_pdf(
    db: Session = Depends(get_db)
):
    file = generate_contract_pdf(db)

    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=contract_report.pdf"
        },
    )


@router.get("/obligations/pdf")
def obligation_pdf(
    db: Session = Depends(get_db)
):
    file = generate_obligation_pdf(db)

    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=obligation_report.pdf"
        },
    )


@router.get("/renewals/pdf")
def renewal_pdf(
    db: Session = Depends(get_db)
):
    file = generate_renewal_pdf(db)

    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=renewal_report.pdf"
        },
    )


@router.get("/compliance/pdf")
def compliance_pdf(
    db: Session = Depends(get_db)
):
    file = generate_compliance_pdf(db)

    return StreamingResponse(
        file,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=compliance_report.pdf"
        },
    )


# =========================================================
# EXCEL REPORTS
# =========================================================

@router.get("/contracts/excel")
def contract_excel(
    db: Session = Depends(get_db)
):
    file = generate_contract_excel(db)

    return StreamingResponse(
        file,
        media_type=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=contract_report.xlsx"
        },
    )


@router.get("/obligations/excel")
def obligation_excel(
    db: Session = Depends(get_db)
):
    file = generate_obligation_excel(db)

    return StreamingResponse(
        file,
        media_type=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=obligation_report.xlsx"
        },
    )


@router.get("/renewals/excel")
def renewal_excel(
    db: Session = Depends(get_db)
):
    file = generate_renewal_excel(db)

    return StreamingResponse(
        file,
        media_type=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=renewal_report.xlsx"
        },
    )


@router.get("/compliance/excel")
def compliance_excel(
    db: Session = Depends(get_db)
):
    file = generate_compliance_excel(db)

    return StreamingResponse(
        file,
        media_type=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                "attachment; filename=compliance_report.xlsx"
        },
    )


# =========================================================
# REPORT CRUD
# =========================================================

@router.post(
    "",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED
)
def create_report(
    data: ReportCreate,
    db: Session = Depends(get_db)
):
    report = Report(
        **data.model_dump()
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


@router.get(
    "",
    response_model=list[ReportResponse]
)
def get_reports(
    db: Session = Depends(get_db)
):
    return db.query(Report).all()


# IMPORTANT:
# Keep all named routes above /{report_id}.
# Otherwise /risk, /contracts/report, etc.
# can be incorrectly matched as report_id.


@router.get(
    "/{report_id}",
    response_model=ReportResponse
)
def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    report = (
        db.query(Report)
        .filter(
            Report.id == report_id
        )
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found",
        )

    return report


@router.put(
    "/{report_id}",
    response_model=ReportResponse
)
def update_report(
    report_id: int,
    data: ReportCreate,
    db: Session = Depends(get_db)
):
    report = (
        db.query(Report)
        .filter(
            Report.id == report_id
        )
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found",
        )

    for key, value in data.model_dump().items():
        setattr(
            report,
            key,
            value
        )

    db.commit()
    db.refresh(report)

    return report


@router.delete(
    "/{report_id}"
)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    report = (
        db.query(Report)
        .filter(
            Report.id == report_id
        )
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found",
        )

    db.delete(report)
    db.commit()

    return {
        "message":
            f"Report {report_id} deleted successfully"
    }