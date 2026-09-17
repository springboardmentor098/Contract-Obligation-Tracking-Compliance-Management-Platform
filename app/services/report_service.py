from io import BytesIO

from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from datetime import date, timedelta

from sqlalchemy import func, or_
from sqlalchemy.orm import aliased
from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.renewal import Renewal
from app.models.compliance import ComplianceRecord


def get_dashboard_summary(db: Session):
    today = date.today()

    total_contracts = db.query(func.count(Contract.id)).scalar() or 0

    active_contracts = (
        db.query(func.count(Contract.id))
        .filter(Contract.status == "Active")
        .scalar()
        or 0
    )

    draft_contracts = (
        db.query(func.count(Contract.id))
        .filter(Contract.status == "Draft")
        .scalar()
        or 0
    )

    contracts_under_review = (
        db.query(func.count(Contract.id))
        .filter(Contract.status == "Under Review")
        .scalar()
        or 0
    )

    expired_contracts = (
        db.query(func.count(Contract.id))
        .filter(
            (Contract.status == "Expired")
            | (Contract.end_date < today)
        )
        .scalar()
        or 0
    )

    total_obligations = (
        db.query(func.count(Obligation.id)).scalar() or 0
    )

    pending_obligations = (
        db.query(func.count(Obligation.id))
        .filter(Obligation.status == "Pending")
        .scalar()
        or 0
    )

    completed_obligations = (
        db.query(func.count(Obligation.id))
        .filter(Obligation.status == "Completed")
        .scalar()
        or 0
    )

    overdue_obligations = (
        db.query(func.count(Obligation.id))
        .filter(
            Obligation.due_date < today,
            Obligation.status != "Completed"
        )
        .scalar()
        or 0
    )

    upcoming_renewals = (
        db.query(func.count(Renewal.id))
        .filter(
            Renewal.renewal_date >= today,
            Renewal.renewal_status == "Upcoming"
        )
        .scalar()
        or 0
    )

    compliant_contracts = (
        db.query(func.count(func.distinct(ComplianceRecord.contract_id)))
        .filter(ComplianceRecord.status == "Compliant")
        .scalar()
        or 0
    )

    non_compliant_contracts = (
        db.query(func.count(func.distinct(ComplianceRecord.contract_id)))
        .filter(ComplianceRecord.status == "Non-Compliant")
        .scalar()
        or 0
    )

    high_risk_contracts = (
        db.query(func.count(func.distinct(ComplianceRecord.contract_id)))
        .filter(ComplianceRecord.risk_level == "High")
        .scalar()
        or 0
    )

    return {
        "total_contracts": total_contracts,
        "active_contracts": active_contracts,
        "draft_contracts": draft_contracts,
        "contracts_under_review": contracts_under_review,
        "upcoming_renewals": upcoming_renewals,
        "expired_contracts": expired_contracts,
        "total_obligations": total_obligations,
        "pending_obligations": pending_obligations,
        "overdue_obligations": overdue_obligations,
        "completed_obligations": completed_obligations,
        "compliant_contracts": compliant_contracts,
        "non_compliant_contracts": non_compliant_contracts,
        "high_risk_contracts": high_risk_contracts,
    }
def get_contract_stats(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
    status: str | None = None,
    category: str | None = None
):
    query = db.query(Contract)

    if start_date:
        query = query.filter(Contract.end_date >= start_date)

    if end_date:
        query = query.filter(Contract.start_date <= end_date)

    if status:
        query = query.filter(Contract.status == status)

    if category:
        query = query.filter(Contract.category == category)

    contracts = query.all()

    total = len(contracts)

    active = sum(
        1 for contract in contracts
        if contract.status == "Active"
    )

    draft = sum(
        1 for contract in contracts
        if contract.status == "Draft"
    )

    under_review = sum(
        1 for contract in contracts
        if contract.status == "Under Review"
    )

    approved = sum(
        1 for contract in contracts
        if contract.status == "Approved"
    )

    expired = sum(
        1 for contract in contracts
        if contract.status == "Expired"
    )

    terminated = sum(
        1 for contract in contracts
        if contract.status == "Terminated"
    )

    by_category = {}

    for contract in contracts:
        by_category[contract.category] = (
            by_category.get(contract.category, 0) + 1
        )

    return {
        "total": total,
        "active": active,
        "draft": draft,
        "under_review": under_review,
        "approved": approved,
        "expired": expired,
        "terminated": terminated,
        "by_category": by_category,
    }
def get_obligation_stats(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None
):
    today = date.today()

    query = db.query(Obligation)

    if start_date:
        query = query.filter(Obligation.due_date >= start_date)

    if end_date:
        query = query.filter(Obligation.due_date <= end_date)

    obligations = query.all()

    total = len(obligations)

    pending = sum(
        1 for obligation in obligations
        if obligation.status == "Pending"
    )

    in_progress = sum(
        1 for obligation in obligations
        if obligation.status == "In Progress"
    )

    completed = sum(
        1 for obligation in obligations
        if obligation.status == "Completed"
    )

    delayed = sum(
        1 for obligation in obligations
        if obligation.status == "Delayed"
    )

    overdue = sum(
        1 for obligation in obligations
        if obligation.due_date
        and obligation.due_date < today
        and obligation.status != "Completed"
    )

    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "delayed": delayed,
        "overdue": overdue,
    }
def get_renewal_stats(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None
):
    today = date.today()

    query = db.query(Renewal)

    if start_date:
        query = query.filter(Renewal.renewal_date >= start_date)

    if end_date:
        query = query.filter(Renewal.renewal_date <= end_date)

    renewals = query.all()

    upcoming = sum(
        1 for renewal in renewals
        if renewal.renewal_status == "Upcoming"
    )

    in_progress = sum(
        1 for renewal in renewals
        if renewal.renewal_status == "In Progress"
    )

    renewed = sum(
        1 for renewal in renewals
        if renewal.renewal_status == "Renewed"
    )

    expired = sum(
        1 for renewal in renewals
        if renewal.renewal_status == "Expired"
    )

    cancelled = sum(
        1 for renewal in renewals
        if renewal.renewal_status == "Cancelled"
    )

    approaching_query = db.query(Contract).filter(
        Contract.end_date >= today,
        Contract.end_date <= today + timedelta(days=90)
    )

    if start_date:
        approaching_query = approaching_query.filter(
            Contract.end_date >= start_date
        )

    if end_date:
        approaching_query = approaching_query.filter(
            Contract.end_date <= end_date
        )

    approaching_rows = (
        approaching_query
        .order_by(Contract.end_date)
        .all()
    )

    approaching_expiry = []

    for contract in approaching_rows:
        days_remaining = (contract.end_date - today).days

        approaching_expiry.append({
            "contract_id": contract.id,
            "contract_number": contract.contract_number,
            "expiry_date": contract.end_date.isoformat(),
            "days_remaining": days_remaining,
        })

    return {
        "upcoming": upcoming,
        "in_progress": in_progress,
        "renewed": renewed,
        "expired": expired,
        "cancelled": cancelled,
        "approaching_expiry": approaching_expiry,
    }
def get_compliance_stats(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None
):
    query = db.query(ComplianceRecord)

    if start_date:
        query = query.filter(
            ComplianceRecord.evaluated_at >= start_date
        )

    if end_date:
        query = query.filter(
            ComplianceRecord.evaluated_at
            < end_date + timedelta(days=1)
        )

    records = query.all()

    total_evaluated = len(
        set(record.contract_id for record in records)
    )

    compliant = len(
        set(
            record.contract_id
            for record in records
            if record.status == "Compliant"
        )
    )

    pending = len(
        set(
            record.contract_id
            for record in records
            if record.status == "Pending"
        )
    )

    delayed = len(
        set(
            record.contract_id
            for record in records
            if record.status == "Delayed"
        )
    )

    non_compliant = len(
        set(
            record.contract_id
            for record in records
            if record.status == "Non-Compliant"
        )
    )

    high_risk = len(
        set(
            record.contract_id
            for record in records
            if record.risk_level == "High"
        )
    )

    scores = [
        float(record.compliance_score)
        for record in records
        if record.compliance_score is not None
    ]

    average_score = (
        round(sum(scores) / len(scores), 2)
        if scores
        else None
    )

    return {
        "total_evaluated": total_evaluated,
        "compliant": compliant,
        "pending": pending,
        "delayed": delayed,
        "non_compliant": non_compliant,
        "high_risk": high_risk,
        "average_compliance_score": average_score,
    }
def get_risk_summary(db: Session):
    latest_compliance_date = (
        db.query(
            ComplianceRecord.contract_id,
            func.max(ComplianceRecord.evaluated_at).label(
                "latest_evaluated_at"
            )
        )
        .group_by(ComplianceRecord.contract_id)
        .subquery()
    )

    LatestCompliance = aliased(ComplianceRecord)

    overdue_count = (
        db.query(func.count(Obligation.id))
        .filter(
            Obligation.contract_id == Contract.id,
            Obligation.due_date < date.today(),
            Obligation.status != "Completed"
        )
        .correlate(Contract)
        .scalar_subquery()
    )

    rows = (
        db.query(
            Contract.id,
            Contract.contract_number,
            LatestCompliance.risk_level,
            LatestCompliance.compliance_score,
            overdue_count.label("overdue_obligations")
        )
        .outerjoin(
            latest_compliance_date,
            latest_compliance_date.c.contract_id == Contract.id
        )
        .outerjoin(
            LatestCompliance,
            (LatestCompliance.contract_id == Contract.id)
            & (
                LatestCompliance.evaluated_at
                == latest_compliance_date.c.latest_evaluated_at
            )
        )
        .filter(
            or_(
                LatestCompliance.risk_level == "High",
                LatestCompliance.status == "Non-Compliant",
                overdue_count > 0
            )
        )
        .order_by(
            overdue_count.desc(),
            LatestCompliance.risk_level.desc()
        )
        .all()
    )

    return {
        "contracts_needing_attention": [
            {
                "contract_id": contract_id,
                "contract_number": contract_number,
                "risk_level": risk_level or "Unknown",
                "overdue_obligations": overdue_obligations or 0,
                "compliance_score": compliance_score,
            }
            for (
                contract_id,
                contract_number,
                risk_level,
                compliance_score,
                overdue_obligations
            ) in rows
        ]
    }
def get_contract_report_data(db: Session):
    contracts = (
        db.query(Contract)
        .order_by(Contract.id)
        .all()
    )

    rows = []

    for contract in contracts:
        rows.append({
            "Contract Number": contract.contract_number,
            "Title": contract.title,
            "Category": contract.category,
            "Status": contract.status,
            "Start Date": contract.start_date.isoformat(),
            "End Date": contract.end_date.isoformat(),
        })

    return rows


def get_obligation_report_data(db: Session):
    obligations = (
        db.query(Obligation)
        .order_by(Obligation.id)
        .all()
    )

    rows = []

    for obligation in obligations:
        rows.append({
            "Obligation ID": obligation.id,
            "Contract ID": obligation.contract_id,
            "Title": obligation.title,
            "Type": obligation.obligation_type,
            "Due Date": obligation.due_date.isoformat(),
            "Status": obligation.status,
        })

    return rows


def get_renewal_report_data(db: Session):
    renewals = (
        db.query(Renewal)
        .order_by(Renewal.id)
        .all()
    )

    rows = []

    for renewal in renewals:
        rows.append({
            "Renewal ID": renewal.id,
            "Contract ID": renewal.contract_id,
            "Renewal Date": renewal.renewal_date.isoformat(),
            "Previous Expiry": renewal.previous_expiry_date.isoformat() if renewal.previous_expiry_date else "",
            "New Expiry": renewal.new_expiry_date.isoformat() if renewal.new_expiry_date else "",
            "Status": renewal.renewal_status,
        })

    return rows


def get_compliance_report_data(db: Session):
    records = (
        db.query(ComplianceRecord)
        .order_by(ComplianceRecord.id)
        .all()
    )

    rows = []

    for record in records:
        rows.append({
            "Contract ID": record.contract_id,
            "Status": record.status,
            "Compliance Score": record.compliance_score,
            "Risk Level": record.risk_level,
            "Evaluated At": (
                record.evaluated_at.isoformat()
                if record.evaluated_at
                else ""
            ),
        })

    return rows


def generate_pdf_report(
    title: str,
    rows: list[dict]
):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(title, styles["Title"])
    )

    elements.append(
        Paragraph(
            f"Generated Date: {date.today().isoformat()}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 15))

    elements.append(
        Paragraph(
            f"Total Records: {len(rows)}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 10))

    if rows:
        headers = list(rows[0].keys())

        table_data = [headers]

        for row in rows:
            table_data.append(
                [str(row.get(header, "")) for header in headers]
            )

        table = Table(
            table_data,
            repeatRows=1
        )

        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                    colors.whitesmoke,
                    colors.lightgrey
                ]),
            ])
        )

        elements.append(table)
    else:
        elements.append(
            Paragraph(
                "No records available.",
                styles["Normal"]
            )
        )

    document.build(elements)

    buffer.seek(0)

    return buffer


def generate_excel_report(
    title: str,
    rows: list[dict]
):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = title[:31]

    if rows:
        headers = list(rows[0].keys())

        worksheet.append(headers)

        for row in rows:
            worksheet.append(
                [row.get(header, "") for header in headers]
            )

        for cell in worksheet[1]:
            cell.font = cell.font.copy(bold=True)

        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter

            for cell in column:
                value = str(cell.value or "")
                max_length = max(max_length, len(value))

            worksheet.column_dimensions[
                column_letter
            ].width = min(max_length + 2, 40)

    else:
        worksheet.append(["No records available"])

    buffer = BytesIO()

    workbook.save(buffer)

    buffer.seek(0)

    return buffer
