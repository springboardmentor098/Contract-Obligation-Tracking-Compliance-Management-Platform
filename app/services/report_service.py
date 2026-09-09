from datetime import date, timedelta
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from sqlalchemy import func

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
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
from app.services.compliance_service import calculate_compliance


# =========================================================
# DASHBOARD SUMMARY
# =========================================================

def get_dashboard_summary(db: Session):

    # -----------------------------------------------------
    # Contract Statistics
    # -----------------------------------------------------

    total_contracts = db.query(Contract).count()

    active_contracts = db.query(Contract).filter(
        Contract.status == "Active"
    ).count()

    draft_contracts = db.query(Contract).filter(
        Contract.status == "Draft"
    ).count()

    under_review_contracts = db.query(Contract).filter(
        Contract.status == "Under Review"
    ).count()

    approved_contracts = db.query(Contract).filter(
        Contract.status == "Approved"
    ).count()

    expired_contracts = db.query(Contract).filter(
        Contract.status == "Expired"
    ).count()

    terminated_contracts = db.query(Contract).filter(
        Contract.status == "Terminated"
    ).count()

    # -----------------------------------------------------
    # Obligation Statistics
    # -----------------------------------------------------

    total_obligations = db.query(Obligation).count()

    pending_obligations = db.query(Obligation).filter(
        Obligation.status == "Pending"
    ).count()

    in_progress_obligations = db.query(Obligation).filter(
        Obligation.status == "In Progress"
    ).count()

    completed_obligations = db.query(Obligation).filter(
        Obligation.status == "Completed"
    ).count()

    delayed_obligations = db.query(Obligation).filter(
        Obligation.status == "Delayed"
    ).count()

    overdue_obligations = db.query(Obligation).filter(
        Obligation.due_date < date.today(),
        Obligation.status != "Completed"
    ).count()

    # -----------------------------------------------------
    # Renewal Statistics
    # -----------------------------------------------------

    upcoming_renewals = db.query(Renewal).filter(
        Renewal.status == "Upcoming"
    ).count()

    in_progress_renewals = db.query(Renewal).filter(
        Renewal.status == "In Progress"
    ).count()

    renewed_renewals = db.query(Renewal).filter(
        Renewal.status == "Renewed"
    ).count()

    expired_renewals = db.query(Renewal).filter(
        Renewal.status == "Expired"
    ).count()

    cancelled_renewals = db.query(Renewal).filter(
        Renewal.status == "Cancelled"
    ).count()

    # -----------------------------------------------------
    # Compliance Statistics
    # -----------------------------------------------------

    contracts = db.query(Contract).all()

    compliant = 0
    pending = 0
    delayed = 0
    non_compliant = 0
    high_risk = 0

    total_score = 0

    for contract in contracts:

        compliance = calculate_compliance(
            contract,
            db
        )

        compliance_status = compliance["compliance_status"]

        total_score += compliance["compliance_score"]

        if compliance_status == "Compliant":
            compliant += 1

        elif compliance_status == "Pending":
            pending += 1

        elif compliance_status == "Delayed":
            delayed += 1

        elif compliance_status == "Non-Compliant":
            non_compliant += 1

        elif compliance_status == "High Risk":
            high_risk += 1

    if contracts:
        average_score = round(
            total_score / len(contracts),
            2
        )
    else:
        average_score = 0

    return {
        "contracts": {
            "total": total_contracts,
            "active": active_contracts,
            "draft": draft_contracts,
            "under_review": under_review_contracts,
            "approved": approved_contracts,
            "expired": expired_contracts,
            "terminated": terminated_contracts
        },

        "obligations": {
            "total": total_obligations,
            "pending": pending_obligations,
            "in_progress": in_progress_obligations,
            "completed": completed_obligations,
            "delayed": delayed_obligations,
            "overdue": overdue_obligations
        },

        "renewals": {
            "upcoming": upcoming_renewals,
            "in_progress": in_progress_renewals,
            "renewed": renewed_renewals,
            "expired": expired_renewals,
            "cancelled": cancelled_renewals
        },

        "compliance": {
            "total": len(contracts),
            "compliant": compliant,
            "pending": pending,
            "delayed": delayed,
            "non_compliant": non_compliant,
            "high_risk": high_risk,
            "average_score": average_score
        }
    }


# =========================================================
# CONTRACT ANALYTICS
# =========================================================

def get_contract_summary(
    db: Session,
    status: str | None = None
):

    query = db.query(Contract)

    # Optional status filter
    if status:
        query = query.filter(
            Contract.status == status
        )

    # -----------------------------------------------------
    # Basic Statistics
    # -----------------------------------------------------

    total_contracts = query.count()

    active_contracts = query.filter(
        Contract.status == "Active"
    ).count()

    expired_contracts = query.filter(
        Contract.status == "Expired"
    ).count()

    pending_approval_contracts = query.filter(
        Contract.status == "Under Review"
    ).count()

    # -----------------------------------------------------
    # Group by Status
    # -----------------------------------------------------

    status_results = (
        query.with_entities(
            Contract.status,
            func.count(Contract.id)
        )
        .group_by(Contract.status)
        .all()
    )

    contracts_by_status = {
        status_name: count
        for status_name, count in status_results
    }

    # -----------------------------------------------------
    # Group by Category
    # -----------------------------------------------------

    category_results = (
        query.with_entities(
            Contract.category,
            func.count(Contract.id)
        )
        .group_by(Contract.category)
        .all()
    )

    contracts_by_category = {
        category: count
        for category, count in category_results
    }

    return {
        "total_contracts": total_contracts,
        "active_contracts": active_contracts,
        "expired_contracts": expired_contracts,
        "pending_approval_contracts": pending_approval_contracts,
        "contracts_by_status": contracts_by_status,
        "contracts_by_category": contracts_by_category
    }


# =========================================================
# OBLIGATION ANALYTICS
# =========================================================

def get_obligation_summary(
    db: Session,
    status: str | None = None
):

    query = db.query(Obligation)

    # Optional status filter
    if status:
        query = query.filter(
            Obligation.status == status
        )

    # -----------------------------------------------------
    # Basic Statistics
    # -----------------------------------------------------

    total_obligations = query.count()

    pending_obligations = query.filter(
        Obligation.status == "Pending"
    ).count()

    completed_obligations = query.filter(
        Obligation.status == "Completed"
    ).count()

    in_progress_obligations = query.filter(
        Obligation.status == "In Progress"
    ).count()

    delayed_obligations = query.filter(
        Obligation.status == "Delayed"
    ).count()

    overdue_obligations = query.filter(
        Obligation.due_date < date.today(),
        Obligation.status != "Completed"
    ).count()

    # -----------------------------------------------------
    # Group by Status
    # -----------------------------------------------------

    status_results = (
        query.with_entities(
            Obligation.status,
            func.count(Obligation.id)
        )
        .group_by(Obligation.status)
        .all()
    )

    obligations_by_status = {
        status_name: count
        for status_name, count in status_results
    }

    return {
        "total_obligations": total_obligations,
        "pending_obligations": pending_obligations,
        "completed_obligations": completed_obligations,
        "overdue_obligations": overdue_obligations,
        "in_progress_obligations": in_progress_obligations,
        "delayed_obligations": delayed_obligations,
        "obligations_by_status": obligations_by_status
    }


# =========================================================
# RENEWAL ANALYTICS
# =========================================================

def get_renewal_summary(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None
):

    query = db.query(Renewal)

    # -----------------------------------------------------
    # Date Range Filter
    # -----------------------------------------------------

    if start_date:
        query = query.filter(
            Renewal.renewal_date >= start_date
        )

    if end_date:
        query = query.filter(
            Renewal.renewal_date <= end_date
        )

    # -----------------------------------------------------
    # Renewal Statistics
    # -----------------------------------------------------

    upcoming = query.filter(
        Renewal.status == "Upcoming"
    ).count()

    in_progress = query.filter(
        Renewal.status == "In Progress"
    ).count()

    renewed = query.filter(
        Renewal.status == "Renewed"
    ).count()

    expired = query.filter(
        Renewal.status == "Expired"
    ).count()

    cancelled = query.filter(
        Renewal.status == "Cancelled"
    ).count()

    renewals_in_date_range = query.count()

    # -----------------------------------------------------
    # Upcoming Contract Expiry
    # -----------------------------------------------------

    today = date.today()

    future_date = today + timedelta(days=90)

    contracts = db.query(Contract).filter(
        Contract.end_date >= today,
        Contract.end_date <= future_date
    ).order_by(
        Contract.end_date
    ).all()

    upcoming_contracts = []

    immediate_attention = []

    for contract in contracts:

        days_remaining = (
            contract.end_date - today
        ).days

        renewal_data = {
            "contract_id": contract.id,
            "contract_number": contract.contract_number,
            "expiry_date": contract.end_date,
            "days_remaining": days_remaining
        }

        upcoming_contracts.append(
            renewal_data
        )

        # Contracts expiring within 30 days
        if days_remaining <= 30:
            immediate_attention.append(
                renewal_data
            )

    return {
        "upcoming": upcoming,
        "in_progress": in_progress,
        "renewed": renewed,
        "expired": expired,
        "cancelled": cancelled,
        "upcoming_contracts": upcoming_contracts,
        "immediate_attention": immediate_attention,
        "renewals_in_date_range": renewals_in_date_range
    }


# =========================================================
# COMPLIANCE ANALYTICS
# =========================================================

def get_compliance_summary_report(
    db: Session
):

    contracts = db.query(Contract).all()

    total_contracts = len(contracts)

    compliant = 0
    pending = 0
    delayed = 0
    non_compliant = 0
    high_risk = 0

    total_score = 0

    for contract in contracts:

        compliance = calculate_compliance(
            contract,
            db
        )

        compliance_status = compliance[
            "compliance_status"
        ]

        total_score += compliance[
            "compliance_score"
        ]

        if compliance_status == "Compliant":
            compliant += 1

        elif compliance_status == "Pending":
            pending += 1

        elif compliance_status == "Delayed":
            delayed += 1

        elif compliance_status == "Non-Compliant":
            non_compliant += 1

        elif compliance_status == "High Risk":
            high_risk += 1

    if total_contracts > 0:

        average_score = round(
            total_score / total_contracts,
            2
        )

    else:

        average_score = 0

    return {
        "total_contracts": total_contracts,
        "compliant": compliant,
        "pending": pending,
        "delayed": delayed,
        "non_compliant": non_compliant,
        "high_risk": high_risk,
        "average_score": average_score
    }


# =========================================================
# RISK ANALYSIS
# =========================================================

def get_risk_report(db: Session):

    contracts = db.query(Contract).all()

    results = []

    for contract in contracts:

        compliance = calculate_compliance(
            contract,
            db
        )

        risk_level = compliance[
            "risk_level"
        ]

        if risk_level in [
            "Medium",
            "High"
        ]:

            results.append({
                "contract_id": contract.id,
                "contract_number": contract.contract_number,
                "risk_level": risk_level,
                "overdue_obligations": compliance[
                    "overdue_obligations"
                ],
                "compliance_score": compliance[
                    "compliance_score"
                ]
            })

    return results

# =========================================================
# PDF REPORT GENERATION
# =========================================================

def _create_pdf(title: str, summary_data: dict, columns: list[str]):
    """
    Creates a professional PDF report from summary data.
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=9,
        textColor=colors.grey,
        spaceAfter=18,
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=8,
        spaceAfter=8,
    )

    story = []

    # -----------------------------------------------------
    # Header
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "ContractIQ",
            title_style
        )
    )

    story.append(
        Paragraph(
            title,
            heading_style
        )
    )

    story.append(
        Paragraph(
            f"Generated on: {date.today().strftime('%d %B %Y')}",
            subtitle_style
        )
    )

    # -----------------------------------------------------
    # Summary Table
    # -----------------------------------------------------

    table_data = [
        ["Metric", "Value"]
    ]

    for key, value in summary_data.items():

        # Skip nested dictionaries/lists
        if isinstance(value, (dict, list)):
            continue

        formatted_key = key.replace("_", " ").title()

        table_data.append([
            formatted_key,
            str(value)
        ])

    table = Table(
        table_data,
        colWidths=[105 * mm, 55 * mm]
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#2563EB")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "ALIGN",
                (1, 1),
                (1, -1),
                "CENTER"
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#CBD5E1")
            ),
            (
                "BACKGROUND",
                (0, 1),
                (-1, -1),
                colors.HexColor("#F8FAFC")
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, -1),
                "Helvetica"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
        ])
    )

    story.append(table)

    # -----------------------------------------------------
    # Detailed Sections
    # -----------------------------------------------------

    for key, value in summary_data.items():

        if not isinstance(value, dict):
            continue

        story.append(
            Spacer(1, 12)
        )

        story.append(
            Paragraph(
                key.replace("_", " ").title(),
                heading_style
            )
        )

        nested_data = [
            ["Item", "Count"]
        ]

        for nested_key, nested_value in value.items():

            nested_data.append([
                nested_key.replace("_", " ").title(),
                str(nested_value)
            ])

        nested_table = Table(
            nested_data,
            colWidths=[105 * mm, 55 * mm]
        )

        nested_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#475569")
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CBD5E1")
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
            ])
        )

        story.append(nested_table)

    document.build(story)

    buffer.seek(0)

    return buffer


# =========================================================
# CONTRACT PDF
# =========================================================

def generate_contract_pdf(db: Session):

    data = get_contract_summary(db)

    return _create_pdf(
        title="Contract Analytics Report",
        summary_data=data,
        columns=["Metric", "Value"]
    )


# =========================================================
# OBLIGATION PDF
# =========================================================

def generate_obligation_pdf(db: Session):

    data = get_obligation_summary(db)

    return _create_pdf(
        title="Obligation Analytics Report",
        summary_data=data,
        columns=["Metric", "Value"]
    )


# =========================================================
# RENEWAL PDF
# =========================================================

def generate_renewal_pdf(db: Session):

    data = get_renewal_summary(db)

    return _create_pdf(
        title="Renewal Analytics Report",
        summary_data=data,
        columns=["Metric", "Value"]
    )


# =========================================================
# COMPLIANCE PDF
# =========================================================

def generate_compliance_pdf(db: Session):

    data = get_compliance_summary_report(db)

    return _create_pdf(
        title="Compliance Analytics Report",
        summary_data=data,
        columns=["Metric", "Value"]
    )

# =========================================================
# EXCEL REPORT GENERATION
# =========================================================

def _create_excel(
    title: str,
    summary_data: dict
):
    """
    Creates a formatted Excel report.
    """

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Report"

    # -----------------------------------------------------
    # Title
    # -----------------------------------------------------

    worksheet["A1"] = "ContractIQ"
    worksheet["A1"].font = Font(
        bold=True,
        size=20
    )

    worksheet["A2"] = title
    worksheet["A2"].font = Font(
        bold=True,
        size=14
    )

    worksheet["A3"] = (
        f"Generated on: {date.today().strftime('%d %B %Y')}"
    )

    # -----------------------------------------------------
    # Header
    # -----------------------------------------------------

    worksheet["A5"] = "Metric"
    worksheet["B5"] = "Value"

    header_fill = PatternFill(
        fill_type="solid",
        fgColor="2563EB"
    )

    header_font = Font(
        bold=True,
        color="FFFFFF"
    )

    for cell in worksheet[5]:

        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(
            horizontal="center"
        )

    # -----------------------------------------------------
    # Summary Data
    # -----------------------------------------------------

    row = 6

    for key, value in summary_data.items():

        if isinstance(value, (dict, list)):
            continue

        worksheet.cell(
            row=row,
            column=1,
            value=key.replace("_", " ").title()
        )

        worksheet.cell(
            row=row,
            column=2,
            value=value
        )

        row += 1

    # -----------------------------------------------------
    # Nested Data
    # -----------------------------------------------------

    for key, value in summary_data.items():

        if not isinstance(value, dict):
            continue

        row += 2

        worksheet.cell(
            row=row,
            column=1,
            value=key.replace("_", " ").title()
        )

        worksheet.cell(
            row=row,
            column=1
        ).font = Font(
            bold=True,
            size=12
        )

        row += 1

        worksheet.cell(
            row=row,
            column=1,
            value="Item"
        )

        worksheet.cell(
            row=row,
            column=2,
            value="Count"
        )

        for col in range(1, 3):

            cell = worksheet.cell(
                row=row,
                column=col
            )

            cell.fill = PatternFill(
                fill_type="solid",
                fgColor="475569"
            )

            cell.font = Font(
                bold=True,
                color="FFFFFF"
            )

            cell.alignment = Alignment(
                horizontal="center"
            )

        row += 1

        for nested_key, nested_value in value.items():

            worksheet.cell(
                row=row,
                column=1,
                value=nested_key.replace(
                    "_",
                    " "
                ).title()
            )

            worksheet.cell(
                row=row,
                column=2,
                value=nested_value
            )

            row += 1

    # -----------------------------------------------------
    # Column Width
    # -----------------------------------------------------

    worksheet.column_dimensions["A"].width = 32
    worksheet.column_dimensions["B"].width = 22

    # -----------------------------------------------------
    # Freeze Header
    # -----------------------------------------------------

    worksheet.freeze_panes = "A6"

    # -----------------------------------------------------
    # Save to Memory
    # -----------------------------------------------------

    buffer = BytesIO()

    workbook.save(buffer)

    buffer.seek(0)

    return buffer


# =========================================================
# CONTRACT EXCEL
# =========================================================

def generate_contract_excel(db: Session):

    data = get_contract_summary(db)

    return _create_excel(
        title="Contract Analytics Report",
        summary_data=data
    )


# =========================================================
# OBLIGATION EXCEL
# =========================================================

def generate_obligation_excel(db: Session):

    data = get_obligation_summary(db)

    return _create_excel(
        title="Obligation Analytics Report",
        summary_data=data
    )


# =========================================================
# RENEWAL EXCEL
# =========================================================

def generate_renewal_excel(db: Session):

    data = get_renewal_summary(db)

    return _create_excel(
        title="Renewal Analytics Report",
        summary_data=data
    )


# =========================================================
# COMPLIANCE EXCEL
# =========================================================

def generate_compliance_excel(db: Session):

    data = get_compliance_summary_report(db)

    return _create_excel(
        title="Compliance Analytics Report",
        summary_data=data
    )