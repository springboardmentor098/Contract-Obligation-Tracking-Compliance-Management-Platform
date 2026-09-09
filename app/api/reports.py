from io import BytesIO
from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.middleware.auth import require_roles
from app.schemas.report import (
    ContractStatistics,
    DashboardSummary,
    DepartmentPerformance,
    ObligationStatistics,
    RenewalStatistics,
    RiskSummary,
    ComplianceStatistics,
)
from app.services.report_service import (
    _contract_statistics,
    _obligation_statistics,
    _renewal_statistics,
    compliance_statistics,
    dashboard_summary,
    department_performance,
    report_rows,
    risk_summary,
)


router = APIRouter(prefix="/reports", tags=["Reports"])
dashboard_router = APIRouter(tags=["Dashboard"])
VIEW_ROLES = (
    "Administrator", "Legal Manager", "Compliance Officer",
    "Contract Manager", "Department Head", "Employee",
)
view_access = require_roles(*VIEW_ROLES)


@router.get("/contracts/summary", response_model=ContractStatistics)
def get_contract_summary(db: Session = Depends(get_db), current_user: dict = Depends(view_access)):
    return _contract_statistics(db)


@router.get("/obligations/summary", response_model=ObligationStatistics)
def get_obligation_summary(db: Session = Depends(get_db), current_user: dict = Depends(view_access)):
    return _obligation_statistics(db)


@router.get("/renewals/summary", response_model=RenewalStatistics)
def get_renewal_summary(days: int = Query(90, gt=0, le=3650), db: Session = Depends(get_db), current_user: dict = Depends(view_access)):
    return _renewal_statistics(db, days)


@router.get("/compliance/summary", response_model=ComplianceStatistics)
def get_compliance_summary(db: Session = Depends(get_db), current_user: dict = Depends(view_access)):
    return compliance_statistics(db)


@router.get("/risk", response_model=list[RiskSummary])
def get_risk_summary(db: Session = Depends(get_db), current_user: dict = Depends(view_access)):
    return risk_summary(db)


@router.get("/departments", response_model=DepartmentPerformance)
def get_department_performance(current_user: dict = Depends(view_access)):
    return department_performance()


@dashboard_router.get("/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary_alias(db: Session = Depends(get_db), current_user: dict = Depends(view_access)):
    return dashboard_summary(db)


def _filename(report_type: str, extension: str) -> str:
    return f"{report_type}-report-{date.today().isoformat()}.{extension}"


def _excel_file(rows: list[dict]) -> BytesIO:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Report"
    headers = list(rows[0]) if rows else ["No data"]
    sheet.append(headers)
    for row in rows:
        sheet.append([row.get(header, "") for header in headers])
    for cell in sheet[1]:
        cell.font = cell.font.copy(bold=True)
    sheet.freeze_panes = "A2"
    output = BytesIO()
    workbook.save(output)
    output.seek(0)
    return output


def _pdf_file(report_type: str, rows: list[dict]) -> BytesIO:
    output = BytesIO()
    document = SimpleDocTemplate(output, pagesize=landscape(letter), rightMargin=24, leftMargin=24)
    styles = getSampleStyleSheet()
    story = [Paragraph(f"{report_type.title()} Report", styles["Title"]), Paragraph(f"Generated: {datetime.utcnow():%Y-%m-%d %H:%M UTC}", styles["Normal"]), Spacer(1, 12)]
    headers = list(rows[0]) if rows else ["Result"]
    values = [[str(row.get(header, "")) for header in headers] for row in rows] or [["No data available"]]
    table = Table([headers] + values, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(table)
    document.build(story)
    output.seek(0)
    return output


def _export(report_type: str, extension: str, db: Session):
    rows = report_rows(db, report_type)
    if extension == "xlsx":
        output = _excel_file(rows)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        output = _pdf_file(report_type, rows)
        media_type = "application/pdf"
    return StreamingResponse(output, media_type=media_type, headers={"Content-Disposition": f'attachment; filename="{_filename(report_type, extension)}"'})


for _report_type in ("contracts", "obligations", "renewals", "compliance"):
    for _extension in ("pdf", "xlsx"):
        path = f"/{_report_type}/export/{'excel' if _extension == 'xlsx' else 'pdf'}"

        def endpoint(db: Session = Depends(get_db), current_user: dict = Depends(view_access), report_type=_report_type, extension=_extension):
            return _export(report_type, extension, db)

        router.add_api_route(path, endpoint, methods=["GET"], name=f"export_{_report_type}_{_extension}")