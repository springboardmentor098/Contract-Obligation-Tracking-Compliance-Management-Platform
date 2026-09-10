from io import BytesIO
from datetime import date

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.renewal import Renewal
from app.services.compliance_service import calculate_contract_compliance


# ============================================================
# PDF HELPERS
# ============================================================

def _build_pdf(title: str, headers: list, rows: list) -> BytesIO:
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()

    elements = [
        Paragraph(title, styles["Title"]),
        Spacer(1, 15),
    ]

    table_data = [headers] + rows

    table = Table(
        table_data,
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
            ]
        )
    )

    elements.append(table)

    document.build(elements)

    buffer.seek(0)
    return buffer


# ============================================================
# EXCEL HELPERS
# ============================================================

def _build_excel(
    sheet_name: str,
    headers: list,
    rows: list,
) -> BytesIO:

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = sheet_name[:31]

    worksheet.append(headers)

    for cell in worksheet[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    for row in rows:
        worksheet.append(row)

    for column in worksheet.columns:
        max_length = 0
        column_letter = column[0].column_letter

        for cell in column:
            value = str(cell.value) if cell.value is not None else ""

            if len(value) > max_length:
                max_length = len(value)

        worksheet.column_dimensions[column_letter].width = min(
            max_length + 2,
            40
        )

    buffer = BytesIO()
    workbook.save(buffer)

    buffer.seek(0)
    return buffer


# ============================================================
# CONTRACT PDF
# ============================================================

def generate_contract_pdf(db: Session) -> BytesIO:

    contracts = (
        db.query(Contract)
        .order_by(Contract.id.asc())
        .all()
    )

    headers = [
        "ID",
        "Contract Code",
        "Title",
        "Status",
        "Risk",
        "Start Date",
        "End Date",
    ]

    rows = []

    for contract in contracts:
        rows.append(
            [
                str(contract.id),
                contract.contract_code,
                contract.title,
                contract.status,
                contract.risk_level,
                str(contract.start_date),
                str(contract.end_date),
            ]
        )

    return _build_pdf(
        "Contract Report",
        headers,
        rows
    )


# ============================================================
# CONTRACT EXCEL
# ============================================================

def generate_contract_excel(db: Session) -> BytesIO:

    contracts = (
        db.query(Contract)
        .order_by(Contract.id.asc())
        .all()
    )

    headers = [
        "ID",
        "Contract Code",
        "Title",
        "Description",
        "Counterparty",
        "Category",
        "Status",
        "Risk Level",
        "Start Date",
        "End Date",
    ]

    rows = []

    for contract in contracts:
        rows.append(
            [
                contract.id,
                contract.contract_code,
                contract.title,
                contract.description,
                contract.counterparty,
                contract.category,
                contract.status,
                contract.risk_level,
                contract.start_date,
                contract.end_date,
            ]
        )

    return _build_excel(
        "Contracts",
        headers,
        rows
    )


# ============================================================
# OBLIGATION PDF
# ============================================================

def generate_obligation_pdf(db: Session) -> BytesIO:

    obligations = (
        db.query(Obligation)
        .order_by(Obligation.due_date.asc())
        .all()
    )

    headers = [
        "ID",
        "Contract ID",
        "Title",
        "Type",
        "Due Date",
        "Status",
        "Priority",
    ]

    rows = []

    for obligation in obligations:
        rows.append(
            [
                str(obligation.id),
                str(obligation.contract_id),
                obligation.title,
                obligation.obligation_type,
                str(obligation.due_date),
                obligation.status,
                obligation.priority or "",
            ]
        )

    return _build_pdf(
        "Obligation Report",
        headers,
        rows
    )


# ============================================================
# OBLIGATION EXCEL
# ============================================================

def generate_obligation_excel(db: Session) -> BytesIO:

    obligations = (
        db.query(Obligation)
        .order_by(Obligation.due_date.asc())
        .all()
    )

    headers = [
        "ID",
        "Contract ID",
        "Assigned To",
        "Title",
        "Description",
        "Obligation Type",
        "Due Date",
        "Status",
        "Completion Date",
        "Frequency",
        "Priority",
        "Evidence Required",
    ]

    rows = []

    for obligation in obligations:
        rows.append(
            [
                obligation.id,
                obligation.contract_id,
                obligation.assigned_to,
                obligation.title,
                obligation.description,
                obligation.obligation_type,
                obligation.due_date,
                obligation.status,
                obligation.completion_date,
                obligation.frequency,
                obligation.priority,
                obligation.evidence_required,
            ]
        )

    return _build_excel(
        "Obligations",
        headers,
        rows
    )


# ============================================================
# RENEWAL PDF
# ============================================================

def generate_renewal_pdf(db: Session) -> BytesIO:

    renewals = (
        db.query(Renewal)
        .order_by(Renewal.renewal_date.asc())
        .all()
    )

    headers = [
        "ID",
        "Contract ID",
        "Renewal Date",
        "Notice Days",
        "Status",
        "Previous Expiry",
        "New Expiry",
    ]

    rows = []

    for renewal in renewals:
        rows.append(
            [
                str(renewal.id),
                str(renewal.contract_id),
                str(renewal.renewal_date),
                str(renewal.notice_days),
                renewal.status,
                str(renewal.previous_expiry_date),
                str(renewal.new_expiry_date)
                if renewal.new_expiry_date
                else "",
            ]
        )

    return _build_pdf(
        "Renewal Report",
        headers,
        rows
    )


# ============================================================
# RENEWAL EXCEL
# ============================================================

def generate_renewal_excel(db: Session) -> BytesIO:

    renewals = (
        db.query(Renewal)
        .order_by(Renewal.renewal_date.asc())
        .all()
    )

    headers = [
        "ID",
        "Contract ID",
        "Assigned To",
        "Renewal Date",
        "Notice Days",
        "Status",
        "Previous Expiry Date",
        "New Expiry Date",
        "Notes",
    ]

    rows = []

    for renewal in renewals:
        rows.append(
            [
                renewal.id,
                renewal.contract_id,
                renewal.assigned_to,
                renewal.renewal_date,
                renewal.notice_days,
                renewal.status,
                renewal.previous_expiry_date,
                renewal.new_expiry_date,
                renewal.notes,
            ]
        )

    return _build_excel(
        "Renewals",
        headers,
        rows
    )


# ============================================================
# COMPLIANCE PDF
# ============================================================

def generate_compliance_pdf(db: Session) -> BytesIO:

    contracts = (
        db.query(Contract)
        .order_by(Contract.id.asc())
        .all()
    )

    headers = [
        "Contract ID",
        "Contract Code",
        "Compliance Status",
        "Score",
        "Total Obligations",
        "Completed",
        "Pending",
        "Delayed",
        "Overdue",
        "Risk",
    ]

    rows = []

    for contract in contracts:

        result = calculate_contract_compliance(
            contract.id,
            db
        )

        rows.append(
            [
                str(contract.id),
                contract.contract_code,
                result["compliance_status"],
                str(result["compliance_score"]),
                str(result["total_obligations"]),
                str(result["completed_obligations"]),
                str(result["pending_obligations"]),
                str(result["delayed_obligations"]),
                str(result["overdue_obligations"]),
                result["risk_level"],
            ]
        )

    return _build_pdf(
        "Compliance Report",
        headers,
        rows
    )


# ============================================================
# COMPLIANCE EXCEL
# ============================================================

def generate_compliance_excel(db: Session) -> BytesIO:

    contracts = (
        db.query(Contract)
        .order_by(Contract.id.asc())
        .all()
    )

    headers = [
        "Contract ID",
        "Contract Code",
        "Compliance Status",
        "Compliance Score",
        "Total Obligations",
        "Completed Obligations",
        "Pending Obligations",
        "Delayed Obligations",
        "Overdue Obligations",
        "Risk Level",
    ]

    rows = []

    for contract in contracts:

        result = calculate_contract_compliance(
            contract.id,
            db
        )

        rows.append(
            [
                contract.id,
                contract.contract_code,
                result["compliance_status"],
                result["compliance_score"],
                result["total_obligations"],
                result["completed_obligations"],
                result["pending_obligations"],
                result["delayed_obligations"],
                result["overdue_obligations"],
                result["risk_level"],
            ]
        )

    return _build_excel(
        "Compliance",
        headers,
        rows
    )