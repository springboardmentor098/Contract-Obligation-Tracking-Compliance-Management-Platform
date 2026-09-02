from datetime import date
from io import BytesIO

from sqlalchemy.orm import Session
from sqlalchemy import func

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from app.models.contracts import Contract
from app.models.obligations import Obligation
from app.models.renewal import Renewal


def get_contract_summary(db: Session):
    total_contracts = db.query(Contract).count()

    active_contracts = db.query(Contract).filter(
        Contract.status == "Active"
    ).count()

    expired_contracts = db.query(Contract).filter(
        Contract.end_date < date.today()
    ).count()

    categories = (
        db.query(
            Contract.category,
            func.count(Contract.id)
        )
        .group_by(Contract.category)
        .all()
    )

    return {
        "total_contracts": total_contracts,
        "active_contracts": active_contracts,
        "expired_contracts": expired_contracts,
        "contracts_by_category": {
            category: count
            for category, count in categories
        }
    }


def get_obligation_summary(db: Session):
    return {
        "total_obligations": db.query(Obligation).count(),
        "completed": db.query(Obligation).filter(
            Obligation.status == "Completed"
        ).count(),
        "pending": db.query(Obligation).filter(
            Obligation.status == "Pending"
        ).count(),
        "delayed": db.query(Obligation).filter(
            Obligation.status == "Delayed"
        ).count(),
        "overdue": db.query(Obligation).filter(
            Obligation.status == "Overdue"
        ).count()
    }


def get_renewal_summary(db: Session):
    return {
        "total_renewals": db.query(Renewal).count(),
        "upcoming": db.query(Renewal).filter(
            Renewal.status == "Upcoming"
        ).count(),
        "renewed": db.query(Renewal).filter(
            Renewal.status == "Renewed"
        ).count(),
        "overdue": db.query(Renewal).filter(
            Renewal.renewal_date < date.today(),
            Renewal.status != "Renewed"
        ).count()
    }


def generate_contract_pdf(db: Session):
    contracts = db.query(Contract).all()

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        title="Contract Report"
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("Contract Report", styles["Title"])
    )

    elements.append(Spacer(1, 20))

    data = [
        [
            "Contract ID",
            "Contract Number",
            "Title",
            "Category",
            "Status"
        ]
    ]

    for contract in contracts:
        data.append([
            str(contract.id),
            contract.contract_number,
            contract.title,
            contract.category,
            contract.status
        ])

    table = Table(data)

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ])
    )

    elements.append(table)

    document.build(elements)

    buffer.seek(0)

    return buffer
from openpyxl import Workbook


def generate_contract_excel(db: Session):
    contracts = db.query(Contract).all()

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Contracts"

    sheet.append([
        "Contract ID",
        "Contract Number",
        "Title",
        "Category",
        "Status"
    ])

    for contract in contracts:
        sheet.append([
            contract.id,
            contract.contract_number,
            contract.title,
            contract.category,
            contract.status
        ])

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    return buffer