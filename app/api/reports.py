from datetime import date
from io import BytesIO
from typing import Callable

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.styles import Font
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user
from app.database import get_db
from app.models.user import User
from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.renewal import Renewal
from app.services.report_service import (
    dashboard_summary,
    contract_summary,
    obligation_summary,
    renewal_summary,
    compliance_summary,
    overdue_obligations,
    risk_summary,
)
from app.models.report import Report, ReportType, ReportFormat

router = APIRouter(tags=["Reports & Dashboard"])


def _excel_response(title: str, rows: list[list], filename: str) -> StreamingResponse:
    wb = Workbook()
    ws = wb.active
    ws.title = title[:31]
    for row_index, row in enumerate(rows, start=1):
        for col_index, value in enumerate(row, start=1):
            cell = ws.cell(row=row_index, column=col_index, value=value)
            if row_index == 1:
                cell.font = Font(bold=True)
    ws.freeze_panes = "A2"
    for column in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in column)
        ws.column_dimensions[column[0].column_letter].width = min(max_len + 2, 45)
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _pdf_response(title: str, rows: list[list], filename: str) -> StreamingResponse:
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=landscape(A4), rightMargin=24, leftMargin=24, topMargin=24, bottomMargin=24)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]), Spacer(1, 12)]
    table = Table(rows, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
    ]))
    story.append(table)
    doc.build(story)
    output.seek(0)
    return StreamingResponse(output, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


def _contract_rows(db: Session):
    return [["Contract #", "Title", "Category", "Status", "Start Date", "End Date"]] + [
        [c.contract_number, c.title, c.category.value, c.status.value, c.start_date.isoformat(), c.end_date.isoformat()]
        for c in db.query(Contract).order_by(Contract.end_date.asc()).all()
    ]


def _obligation_rows(db: Session):
    return [["ID", "Contract #", "Title", "Type", "Due Date", "Status"]] + [
        [o.id, o.contract.contract_number, o.title, o.obligation_type.value, o.due_date.isoformat(), o.status.value]
        for o in db.query(Obligation).order_by(Obligation.due_date.asc()).all()
    ]


def _renewal_rows(db: Session):
    return [["ID", "Contract #", "Renewal Date", "Previous Expiry", "New Expiry", "Status"]] + [
        [r.id, r.contract.contract_number, r.renewal_date.isoformat(), r.previous_expiry_date.isoformat(), r.new_expiry_date.isoformat(), r.status.value]
        for r in db.query(Renewal).order_by(Renewal.renewal_date.asc()).all()
    ]


def _compliance_rows(db: Session):
    rows = [["Contract #", "Title", "Compliance Status", "Score", "Risk", "Overdue Obligations"]]
    for c in db.query(Contract).order_by(Contract.contract_number.asc()).all():
        from app.services.compliance_service import evaluate_contract_compliance
        result = evaluate_contract_compliance(db, c)
        rows.append([c.contract_number, c.title, result.compliance_status.value, result.compliance_score, result.risk_level.value, result.overdue_obligations])
    return rows


@router.get("/dashboard/summary")
def get_dashboard_summary(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return dashboard_summary(db)


@router.get("/reports/contracts/summary")
def get_contract_report(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return contract_summary(db)


@router.get("/reports/obligations/summary")
def get_obligation_report(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return obligation_summary(db)


@router.get("/reports/renewals/summary")
def get_renewal_report(
    upcoming_days: int = Query(30, ge=0, le=3650),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return renewal_summary(db, upcoming_days)


@router.get("/reports/risk")
def get_risk_report(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return risk_summary(db)


@router.get("/dashboard/overdue-obligations")
def get_overdue_obligations(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return {"count": len(overdue_obligations(db)), "items": overdue_obligations(db)}


@router.get("/reports/compliance/summary")
def get_compliance_report(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    return compliance_summary(db)


def _export(kind: str, fmt: str, db: Session, current_user: User):
    builders: dict[str, tuple[str, Callable]] = {
        "contracts": ("Contracts Report", _contract_rows),
        "obligations": ("Obligations Report", _obligation_rows),
        "renewals": ("Renewals Report", _renewal_rows),
        "compliance": ("Compliance Report", _compliance_rows),
    }
    if kind not in builders:
        raise HTTPException(status_code=404, detail="Unknown report type")
    title, builder = builders[kind]
    rows = builder(db)
    extension = "xlsx" if fmt == "excel" else "pdf"
    filename = f"contractiq_{kind}_report.{extension}"
    db.add(Report(
        report_type={
            "contracts": ReportType.CONTRACT_REPORT,
            "obligations": ReportType.OBLIGATION_REPORT,
            "renewals": ReportType.RENEWAL_REPORT,
            "compliance": ReportType.COMPLIANCE_REPORT,
        }[kind],
        report_format=ReportFormat.EXCEL if fmt == "excel" else ReportFormat.PDF,
        generated_by=current_user.id,
    ))
    db.commit()
    return _excel_response(title, rows, filename) if fmt == "excel" else _pdf_response(title, rows, filename)


@router.get("/reports/{kind}/export/{fmt}")
def export_report(
    kind: str,
    fmt: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if fmt not in {"pdf", "excel"}:
        raise HTTPException(status_code=400, detail="Format must be pdf or excel")
    return _export(kind, fmt, db, current_user)
