import csv
import io
import os
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.renewal import Renewal
from app.models.activity import Activity
from app.models.audit_log import AuditLog
from app.models.report import Report
from app.services.compliance_service import calculate_compliance

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to compute and render total page numbers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        # Footer
        footer_text = f"ContractIQ Enterprise Platform • Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 36, 20, footer_text)
        self.drawString(36, 20, "Confidential — Internal Business Use Only")
        self.restoreState()


def sanitize_filename(name: str) -> str:
    """Produce safe ASCII file names."""
    cleaned = re.sub(r"[^\w\s-]", "", name).strip()
    return re.sub(r"[-\s]+", "_", cleaned) or "report"


def get_reports_storage_dir() -> Path:
    """
    Return writable reports directory, supporting local disk and Vercel/serverless /tmp.
    """
    primary = Path("uploads/reports")
    try:
        primary.mkdir(parents=True, exist_ok=True)
        # Test writability
        test_file = primary / ".write_test"
        test_file.touch(exist_ok=True)
        test_file.unlink(missing_ok=True)
        return primary
    except (OSError, PermissionError):
        fallback = Path("/tmp/uploads/reports")
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def gather_report_data(db: Session, report_type: str, user=None) -> dict:
    """
    Aggregate live PostgreSQL data for reports including:
    - Total Contracts
    - Active Contracts
    - Expiring Soon (within 30 days)
    - Expired Contracts
    - Obligations Due & Overdue
    - Renewals (Total & Upcoming)
    - Compliance Status
    - Recent Activities
    - Detailed Records
    """
    today = date.today()
    in_30_days = today + timedelta(days=30)

    # 1. Contracts
    contracts = db.query(Contract).all()
    total_contracts = len(contracts)
    active_contracts = sum(1 for c in contracts if c.status == "Active")
    expiring_soon = sum(
        1 for c in contracts
        if c.end_date and today <= c.end_date <= in_30_days and c.status != "Expired"
    )
    expired_contracts = sum(
        1 for c in contracts
        if (c.end_date and c.end_date < today) or c.status == "Expired"
    )

    # 2. Obligations
    obligations = db.query(Obligation).all()
    obligations_due = sum(
        1 for o in obligations
        if o.status in ["Pending", "In Progress", "Overdue"]
    )
    obligations_overdue = sum(
        1 for o in obligations
        if o.due_date and o.due_date < today and o.status != "Completed"
    )

    # 3. Renewals
    renewals = db.query(Renewal).all()
    total_renewals = len(renewals)
    upcoming_renewals = sum(
        1 for r in renewals
        if r.status == "Upcoming" or (r.renewal_date and r.renewal_date >= today and r.status != "Expired")
    )

    # 4. Compliance Status
    compliance_results = []
    for c in contracts:
        stat = calculate_compliance(c)
        compliance_results.append({
            "contract_id": c.id,
            "contract_title": c.title,
            **stat,
        })

    compliant_count = sum(1 for c in compliance_results if c["status"] == "Compliant")
    partially_compliant = sum(1 for c in compliance_results if c["status"] == "Partially Compliant")
    non_compliant = sum(1 for c in compliance_results if c["status"] == "Non-Compliant")
    avg_score = (
        round(sum(c["compliance_score"] for c in compliance_results) / total_contracts, 1)
        if total_contracts > 0 else 100.0
    )

    # 5. Recent Activities
    raw_activities = db.query(Activity).order_by(Activity.id.desc()).limit(10).all()
    activities_data = []
    if raw_activities:
        for act in raw_activities:
            activities_data.append({
                "id": act.id,
                "activity": act.activity,
                "contract_id": act.contract_id if act.contract_id is not None else "—",
                "user_id": act.user_id if act.user_id is not None else "—",
                "created_at": act.created_at.strftime("%Y-%m-%d %H:%M") if act.created_at else "—",
            })
    else:
        raw_audits = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(10).all()
        for aud in raw_audits:
            activities_data.append({
                "id": aud.id,
                "activity": f"{aud.action} on {aud.table_name} #{aud.record_id}",
                "contract_id": "—",
                "user_id": aud.user_id if aud.user_id is not None else "—",
                "created_at": "—",
            })

    # 6. Detailed Table Records based on report_type
    detailed_headers = []
    detailed_rows = []
    normalized_type = report_type.strip()

    if normalized_type == "Compliance Report":
        detailed_headers = [
            "ID", "Contract Title", "Score", "Status", "Risk Level", "Obligations", "Overdue"
        ]
        detailed_rows = [
            [
                str(c["contract_id"]),
                str(c["contract_title"]),
                f"{c['compliance_score']}%",
                str(c["status"]),
                str(c["risk_level"]),
                str(c["total_obligations"]),
                str(c["overdue"]),
            ]
            for c in compliance_results
        ]
    elif normalized_type == "Obligation Report":
        detailed_headers = [
            "ID", "Contract ID", "Title", "Type", "Priority", "Due Date", "Status"
        ]
        detailed_rows = [
            [
                str(o.id),
                str(o.contract_id),
                str(o.title),
                str(o.obligation_type),
                str(o.priority or "Normal"),
                str(o.due_date),
                str(o.status),
            ]
            for o in obligations
        ]
    elif normalized_type == "Renewal Report":
        detailed_headers = [
            "ID", "Contract ID", "Renewal Date", "Prev Expiry", "New Expiry", "Status"
        ]
        detailed_rows = [
            [
                str(r.id),
                str(r.contract_id),
                str(r.renewal_date),
                str(r.previous_expiry_date),
                str(r.new_expiry_date),
                str(r.status),
            ]
            for r in renewals
        ]
    elif normalized_type == "Audit Report":
        detailed_headers = [
            "ID", "Activity / Action", "Contract ID", "User ID", "Timestamp"
        ]
        detailed_rows = [
            [
                str(a["id"]),
                str(a["activity"]),
                str(a["contract_id"]),
                str(a["user_id"]),
                str(a["created_at"]),
            ]
            for a in activities_data
        ]
    else:  # Contract Report or Executive Summary Report
        detailed_headers = [
            "ID", "Contract #", "Title", "Category", "Department", "Status", "End Date"
        ]
        detailed_rows = [
            [
                str(c.id),
                str(c.contract_number),
                str(c.title),
                str(c.category),
                str(c.department or "—"),
                str(c.status),
                str(c.end_date),
            ]
            for c in contracts
        ]

    generator_name = getattr(user, "full_name", None) or getattr(user, "email", None) or "System Administrator"

    return {
        "report_type": report_type,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
        "generated_by": generator_name,
        "summary": {
            "total_contracts": total_contracts,
            "active_contracts": active_contracts,
            "expiring_soon": expiring_soon,
            "expired_contracts": expired_contracts,
            "obligations_due": obligations_due,
            "obligations_overdue": obligations_overdue,
            "total_renewals": total_renewals,
            "upcoming_renewals": upcoming_renewals,
            "compliant_count": compliant_count,
            "partially_compliant": partially_compliant,
            "non_compliant": non_compliant,
            "avg_score": avg_score,
        },
        "detailed_headers": detailed_headers,
        "detailed_rows": detailed_rows,
        "recent_activities": activities_data,
    }


def generate_csv_report(data: dict) -> bytes:
    """Generate professional CSV report."""
    output = io.StringIO()
    writer = csv.writer(output)

    # 1. Header Information
    writer.writerow(["ContractIQ Enterprise Compliance Platform"])
    writer.writerow(["Report Title", data["report_type"]])
    writer.writerow(["Generated At", data["generated_at"]])
    writer.writerow(["Generated By", data["generated_by"]])
    writer.writerow([])

    # 2. Executive Summary Metrics
    writer.writerow(["=== EXECUTIVE SUMMARY METRICS ==="])
    writer.writerow(["Metric", "Count / Value"])
    summary = data["summary"]
    writer.writerow(["Total Contracts", summary["total_contracts"]])
    writer.writerow(["Active Contracts", summary["active_contracts"]])
    writer.writerow(["Expiring Soon (Next 30 Days)", summary["expiring_soon"]])
    writer.writerow(["Expired Contracts", summary["expired_contracts"]])
    writer.writerow(["Obligations Due", summary["obligations_due"]])
    writer.writerow(["Obligations Overdue", summary["obligations_overdue"]])
    writer.writerow(["Total Renewals", summary["total_renewals"]])
    writer.writerow(["Upcoming Renewals", summary["upcoming_renewals"]])
    writer.writerow(["Compliant Contracts", summary["compliant_count"]])
    writer.writerow(["Partially Compliant Contracts", summary["partially_compliant"]])
    writer.writerow(["Non-Compliant Contracts", summary["non_compliant"]])
    writer.writerow(["Average Compliance Score", f"{summary['avg_score']}%"])
    writer.writerow([])

    # 3. Detailed Records
    writer.writerow([f"=== {data['report_type'].upper()} DETAILED RECORDS ==="])
    if data["detailed_headers"]:
        writer.writerow(data["detailed_headers"])
        for row in data["detailed_rows"]:
            writer.writerow(row)
    else:
        writer.writerow(["No detailed records available."])
    writer.writerow([])

    # 4. Recent Activities Log
    writer.writerow(["=== RECENT SYSTEM ACTIVITIES ==="])
    writer.writerow(["Activity ID", "Activity Description", "Contract ID", "User ID", "Timestamp"])
    for act in data["recent_activities"]:
        writer.writerow([
            act["id"],
            act["activity"],
            act["contract_id"],
            act["user_id"],
            act["created_at"],
        ])

    return output.getvalue().encode("utf-8")


def generate_pdf_report(data: dict) -> bytes:
    """Generate styled PDF report with ContractIQ executive branding."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#64748B"),
    )
    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=14,
        spaceAfter=6,
    )
    card_label = ParagraphStyle(
        "CardLabel",
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#64748B"),
    )
    card_value = ParagraphStyle(
        "CardValue",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#059669"),
    )
    card_value_alert = ParagraphStyle(
        "CardValueAlert",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#DC2626"),
    )
    th_style = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
    )
    td_style = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1E293B"),
    )

    elements = []

    # 1. Header Banner
    header_table = Table(
        [
            [
                Paragraph("<b>ContractIQ</b><br/><font size=8 color='#64748B'>Enterprise Contract Intelligence & Compliance</font>", title_style),
                Paragraph(
                    f"<b>{data['report_type']}</b><br/>"
                    f"<font size=7.5 color='#64748B'>Generated: {data['generated_at']}<br/>"
                    f"By: {data['generated_by']}</font>",
                    ParagraphStyle("MetaRight", parent=subtitle_style, alignment=2),
                ),
            ]
        ],
        colWidths=[320, 220],
    )
    header_table.setStyle(
        TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LINEBELOW", (0, 0), (-1, -1), 1.5, colors.HexColor("#059669")),
        ])
    )
    elements.append(header_table)
    elements.append(Spacer(1, 10))

    # 2. Executive Summary Cards (4 cols x 2 rows = 540pt total)
    elements.append(Paragraph("Executive Overview Metrics", section_style))
    sum_data = data["summary"]

    kpi_cells = [
        [
            [Paragraph("Total Contracts", card_label), Paragraph(str(sum_data["total_contracts"]), card_value)],
            [Paragraph("Active Contracts", card_label), Paragraph(str(sum_data["active_contracts"]), card_value)],
            [Paragraph("Expiring Soon (30d)", card_label), Paragraph(str(sum_data["expiring_soon"]), card_value if sum_data["expiring_soon"] == 0 else card_value_alert)],
            [Paragraph("Expired Contracts", card_label), Paragraph(str(sum_data["expired_contracts"]), card_value if sum_data["expired_contracts"] == 0 else card_value_alert)],
        ],
        [
            [Paragraph("Obligations Due", card_label), Paragraph(str(sum_data["obligations_due"]), card_value)],
            [Paragraph("Renewals Upcoming", card_label), Paragraph(str(sum_data["upcoming_renewals"]), card_value)],
            [Paragraph("Compliance Score", card_label), Paragraph(f"{sum_data['avg_score']}%", card_value)],
            [Paragraph("Non-Compliant", card_label), Paragraph(str(sum_data["non_compliant"]), card_value if sum_data["non_compliant"] == 0 else card_value_alert)],
        ],
    ]

    kpi_table = Table(kpi_cells, colWidths=[135, 135, 135, 135])
    kpi_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#E2E8F0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ])
    )
    elements.append(kpi_table)
    elements.append(Spacer(1, 12))

    # 3. Detailed Records Table
    elements.append(Paragraph(f"{data['report_type']} Details", section_style))
    headers = data["detailed_headers"]
    rows = data["detailed_rows"]

    if headers and rows:
        num_cols = len(headers)
        col_width = 540.0 / num_cols
        widths = [col_width] * num_cols

        # Customize widths for known tables
        if num_cols == 7 and "Score" in headers[2]:  # Compliance Report
            widths = [35, 175, 55, 75, 65, 70, 65]
        elif num_cols == 7 and "Contract #" in headers[1]:  # Contract Report
            widths = [30, 80, 150, 75, 75, 65, 65]
        elif num_cols == 7 and "Priority" in headers[4]:  # Obligation Report
            widths = [30, 60, 160, 80, 65, 75, 70]
        elif num_cols == 6:  # Renewal Report
            widths = [35, 175, 80, 80, 85, 85]

        table_data = [[Paragraph(h, th_style) for h in headers]]
        for row in rows[:50]:  # Cap at 50 to avoid oversized docs
            table_data.append([Paragraph(str(val), td_style) for val in row])

        detail_table = Table(table_data, colWidths=widths, repeatRows=1)
        detail_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
                ("TOPPADDING", (0, 0), (-1, 0), 5),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("TOPPADDING", (0, 1), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ])
        )
        elements.append(detail_table)
    else:
        elements.append(Paragraph("No detailed records found for this category.", td_style))

    elements.append(Spacer(1, 14))

    # 4. Recent Activities Section
    if data["recent_activities"]:
        elements.append(KeepTogether([
            Paragraph("Recent Operational Activity Log", section_style),
            Table(
                [[Paragraph(h, th_style) for h in ["ID", "Activity Description", "Contract ID", "User ID", "Timestamp"]]] +
                [
                    [
                        Paragraph(str(act["id"]), td_style),
                        Paragraph(str(act["activity"]), td_style),
                        Paragraph(str(act["contract_id"]), td_style),
                        Paragraph(str(act["user_id"]), td_style),
                        Paragraph(str(act["created_at"]), td_style),
                    ]
                    for act in data["recent_activities"][:6]
                ],
                colWidths=[35, 235, 75, 65, 130],
                repeatRows=1,
                style=[
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                    ("TOPPADDING", (0, 0), (-1, -1), 3.5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ],
            ),
        ]))

    # Build PDF using NumberedCanvas
    doc.build(elements, canvasmaker=NumberedCanvas)
    return buffer.getvalue()


def save_report_file(file_bytes: bytes, filename: str) -> str:
    """Save bytes to writable report storage and return relative path."""
    storage_dir = get_reports_storage_dir()
    file_path = storage_dir / filename
    file_path.write_bytes(file_bytes)
    return str(file_path).replace("\\", "/")


def get_or_render_report_file(report: Report, format_type: str, db: Session) -> tuple[bytes, str, str]:
    """
    Return (file_bytes, filename, media_type).
    If file exists on disk and matches requested format, serve it.
    If missing (e.g. serverless cold start / Vercel), re-render dynamically from live PostgreSQL data.
    """
    clean_name = sanitize_filename(report.report_name)
    requested_ext = "csv" if format_type.lower() == "csv" else "pdf"
    filename = f"{clean_name}.{requested_ext}"
    media_type = "text/csv; charset=utf-8" if requested_ext == "csv" else "application/pdf"

    # 1. Check if stored file exists and matches extension
    if report.file_path:
        local_path = Path(report.file_path)
        if local_path.is_file() and local_path.suffix.lower() == f".{requested_ext}":
            try:
                return local_path.read_bytes(), filename, media_type
            except OSError:
                pass

    # 2. Dynamic generation fallback (live PostgreSQL data)
    report_data = gather_report_data(db, report.report_type or "General Report")
    if requested_ext == "csv":
        content = generate_csv_report(report_data)
    else:
        content = generate_pdf_report(report_data)

    # Cache locally if directory is writable
    try:
        save_report_file(content, filename)
    except Exception:
        pass

    return content, filename, media_type
