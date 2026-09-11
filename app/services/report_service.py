from datetime import date
from io import BytesIO

from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)

from sqlalchemy import func

from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.renewal import Renewal
from app.services.compliance_service import evaluate_contract_compliance


def _status_count(db, model, status_value):
    return (
        db.query(func.count(model.id))
        .filter(func.lower(model.status) == status_value.lower())
        .scalar()
        or 0
    )


def get_contract_summary(db):
    total = db.query(func.count(Contract.id)).scalar() or 0

    active = _status_count(db, Contract, "Active")
    draft = _status_count(db, Contract, "Draft")
    under_review = _status_count(db, Contract, "Under Review")
    approved = _status_count(db, Contract, "Approved")
    expired = _status_count(db, Contract, "Expired")
    terminated = _status_count(db, Contract, "Terminated")

    categories = (
        db.query(
            Contract.category,
            func.count(Contract.id),
        )
        .group_by(Contract.category)
        .all()
    )

    by_category = {
        category or "Uncategorized": count
        for category, count in categories
    }

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


def get_obligation_summary(db):
    total = db.query(func.count(Obligation.id)).scalar() or 0

    pending = _status_count(db, Obligation, "Pending")
    in_progress = _status_count(db, Obligation, "In Progress")
    completed = _status_count(db, Obligation, "Completed")
    delayed = _status_count(db, Obligation, "Delayed")
    overdue_status = _status_count(db, Obligation, "Overdue")

    today = date.today()

    overdue_by_date = (
        db.query(func.count(Obligation.id))
        .filter(
            Obligation.due_date < today,
            func.lower(Obligation.status) != "completed",
            func.lower(Obligation.status) != "overdue",
        )
        .scalar()
        or 0
    )

    overdue = overdue_status + overdue_by_date

    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "delayed": delayed,
        "overdue": overdue,
    }


def get_renewal_summary(db, upcoming_days=30):
    today = date.today()

    upcoming = (
        db.query(func.count(Contract.id))
        .filter(
            Contract.end_date >= today,
            Contract.end_date <= date.fromordinal(
                today.toordinal() + upcoming_days
            ),
        )
        .scalar()
        or 0
    )

    in_progress = _status_count(db, Renewal, "In Progress")
    renewed = _status_count(db, Renewal, "Renewed")
    expired = _status_count(db, Renewal, "Expired")
    cancelled = _status_count(db, Renewal, "Cancelled")

    contracts = (
        db.query(Contract)
        .filter(
            Contract.end_date >= today,
            Contract.end_date <= date.fromordinal(
                today.toordinal() + upcoming_days
            ),
        )
        .order_by(Contract.end_date.asc())
        .all()
    )

    upcoming_contracts = []

    for contract in contracts:
        days_remaining = (contract.end_date - today).days

        upcoming_contracts.append(
            {
                "contract_id": contract.id,
                "contract_number": contract.contract_number,
                "contract_title": contract.title,
                "expiry_date": contract.end_date.isoformat(),
                "days_remaining": days_remaining,
            }
        )

    return {
        "upcoming": upcoming,
        "in_progress": in_progress,
        "renewed": renewed,
        "expired": expired,
        "cancelled": cancelled,
        "upcoming_contracts": upcoming_contracts,
    }


def get_compliance_summary(db):
    contracts = db.query(Contract).all()

    total = len(contracts)
    compliant = 0
    pending = 0
    delayed = 0
    non_compliant = 0
    high_risk = 0
    scores = []

    for contract in contracts:
        result = evaluate_contract_compliance(contract, db)

        status = result["compliance_status"]

        if status == "Compliant":
            compliant += 1
        elif status == "Pending":
            pending += 1
        elif status == "Delayed":
            delayed += 1
        elif status == "Non-Compliant":
            non_compliant += 1
        elif status == "High Risk":
            high_risk += 1

        scores.append(result["compliance_score"])

    average_score = round(
        sum(scores) / len(scores),
        2,
    ) if scores else 0

    return {
        "total_contracts": total,
        "compliant": compliant,
        "pending": pending,
        "delayed": delayed,
        "non_compliant": non_compliant,
        "high_risk": high_risk,
        "average_score": average_score,
    }


def get_risk_report(db):
    contracts = db.query(Contract).all()

    results = []

    for contract in contracts:
        compliance = evaluate_contract_compliance(
            contract,
            db,
        )

        if compliance["risk_level"] in ("High", "Medium"):
            results.append(
                {
                    "contract_id": contract.id,
                    "contract_number": contract.contract_number,
                    "risk_level": compliance["risk_level"],
                    "overdue_obligations": compliance["overdue_obligations"],
                    "compliance_score": compliance["compliance_score"],
                }
            )

    results.sort(
        key=lambda item: (
            0 if item["risk_level"] == "High" else 1,
            -item["overdue_obligations"],
            item["compliance_score"],
        )
    )

    return results


def get_dashboard_summary(db):
    return {
        "contracts": get_contract_summary(db),
        "obligations": get_obligation_summary(db),
        "renewals": get_renewal_summary(db),
        "compliance": get_compliance_summary(db),
    }


def get_contract_report_rows(db):
    contracts = (
        db.query(Contract)
        .order_by(Contract.id.asc())
        .all()
    )

    return [
        [
            contract.contract_number,
            contract.title,
            contract.category,
            contract.status,
            contract.start_date.isoformat()
            if contract.start_date else "",
            contract.end_date.isoformat()
            if contract.end_date else "",
            str(contract.assigned_to)
            if contract.assigned_to is not None else "",
        ]
        for contract in contracts
    ]


def get_obligation_report_rows(db):
    obligations = (
        db.query(Obligation)
        .order_by(Obligation.id.asc())
        .all()
    )

    return [
        [
            str(obligation.contract_id),
            obligation.title,
            obligation.obligation_type,
            str(obligation.assigned_to)
            if obligation.assigned_to is not None else "",
            obligation.due_date.isoformat()
            if obligation.due_date else "",
            obligation.status,
            obligation.completion_date.isoformat()
            if obligation.completion_date else "",
        ]
        for obligation in obligations
    ]


def get_renewal_report_rows(db):
    renewals = (
        db.query(Renewal)
        .order_by(Renewal.id.asc())
        .all()
    )

    return [
        [
            str(renewal.contract_id),
            renewal.previous_expiry_date.isoformat()
            if renewal.previous_expiry_date else "",
            renewal.renewal_date.isoformat()
            if renewal.renewal_date else "",
            renewal.new_expiry_date.isoformat()
            if renewal.new_expiry_date else "",
            renewal.status,
            str(renewal.assigned_to)
            if renewal.assigned_to is not None else "",
        ]
        for renewal in renewals
    ]


def get_compliance_report_rows(db):
    contracts = db.query(Contract).all()

    rows = []

    for contract in contracts:
        result = evaluate_contract_compliance(contract, db)

        rows.append(
            [
                contract.contract_number,
                result["compliance_status"],
                result["compliance_score"],
                result["overdue_obligations"],
                result["risk_level"],
                date.today().isoformat(),
            ]
        )

    return rows


def generate_excel(title, headers, rows):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = title[:31]

    worksheet.append(headers)

    for row in rows:
        worksheet.append(row)

    for cell in worksheet[1]:
        cell.font = cell.font.copy(bold=True)

    for column in worksheet.columns:
        max_length = 0
        column_letter = column[0].column_letter

        for cell in column:
            value = str(cell.value or "")
            max_length = max(max_length, len(value))

        worksheet.column_dimensions[column_letter].width = min(
            max_length + 2,
            50,
        )

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return output


def generate_pdf(title, headers, rows):
    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    styles = getSampleStyleSheet()

    elements = [
        Paragraph(title, styles["Title"]),
        Spacer(1, 10),
        Paragraph(
            f"Generated: {date.today().isoformat()}",
            styles["Normal"],
        ),
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
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1976D2"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#F5F5F5")],
                ),
            ]
        )
    )

    elements.append(table)

    document.build(elements)

    output.seek(0)

    return output
