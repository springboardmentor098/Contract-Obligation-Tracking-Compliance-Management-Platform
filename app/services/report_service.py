# app/services/report_service.py

from datetime import date, datetime, timedelta
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.contract import Contract
from app.models.obligation import Obligation
from app.models.renewal import Renewal
from app.models.contract_compliance import ContractCompliance
from app.models.user import User


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def _count_by_status(db: Session, model, status_value: str) -> int:
    """
    Generic helper for counting records by status.
    """

    return (
        db.query(func.count(model.id))
        .filter(model.status == status_value)
        .scalar()
        or 0
    )


# =========================================================
# CONTRACT ANALYTICS
# =========================================================

def get_contract_summary(db: Session) -> dict:

    total = (
        db.query(func.count(Contract.id))
        .scalar()
        or 0
    )

    active = _count_by_status(
        db,
        Contract,
        "Active"
    )

    draft = _count_by_status(
        db,
        Contract,
        "Draft"
    )

    under_review = _count_by_status(
        db,
        Contract,
        "Under Review"
    )

    approved = _count_by_status(
        db,
        Contract,
        "Approved"
    )

    expired = _count_by_status(
        db,
        Contract,
        "Expired"
    )

    terminated = _count_by_status(
        db,
        Contract,
        "Terminated"
    )

    categories = (
        db.query(
            Contract.category,
            func.count(Contract.id)
        )
        .group_by(Contract.category)
        .all()
    )

    by_category = {
        category or "Unknown": count
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


# =========================================================
# OBLIGATION ANALYTICS
# =========================================================

def get_obligation_summary(db: Session) -> dict:

    total = (
        db.query(func.count(Obligation.id))
        .scalar()
        or 0
    )

    pending = _count_by_status(
        db,
        Obligation,
        "Pending"
    )

    in_progress = _count_by_status(
        db,
        Obligation,
        "In Progress"
    )

    completed = _count_by_status(
        db,
        Obligation,
        "Completed"
    )

    delayed = _count_by_status(
        db,
        Obligation,
        "Delayed"
    )

    overdue = (
        db.query(func.count(Obligation.id))
        .filter(
            Obligation.due_date < date.today(),
            Obligation.status != "Completed",
        )
        .scalar()
        or 0
    )

    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "delayed": delayed,
        "overdue": overdue,
    }


# =========================================================
# RENEWAL ANALYTICS
# =========================================================

def get_renewal_summary(
    db: Session,
    expiry_days: int = 30
) -> dict:

    upcoming = _count_by_status(
        db,
        Renewal,
        "Upcoming"
    )

    in_progress = _count_by_status(
        db,
        Renewal,
        "In Progress"
    )

    renewed = _count_by_status(
        db,
        Renewal,
        "Renewed"
    )

    expired = _count_by_status(
        db,
        Renewal,
        "Expired"
    )

    cancelled = _count_by_status(
        db,
        Renewal,
        "Cancelled"
    )

    today = date.today()

    expiry_limit = today + timedelta(
        days=expiry_days
    )

    contracts = (
        db.query(Contract)
        .filter(
            Contract.end_date.isnot(None),
            Contract.end_date >= today,
            Contract.end_date <= expiry_limit,
        )
        .order_by(Contract.end_date.asc())
        .all()
    )

    approaching_expiry = []

    for contract in contracts:

        days_remaining = (
            contract.end_date - today
        ).days

        approaching_expiry.append(
            {
                "contract_id": contract.id,
                "contract_number": contract.contract_number,
                "contract_title": contract.title,
                "expiry_date": contract.end_date,
                "days_remaining": days_remaining,
            }
        )

    return {
        "upcoming": upcoming,
        "in_progress": in_progress,
        "renewed": renewed,
        "expired": expired,
        "cancelled": cancelled,
        "approaching_expiry": approaching_expiry,
    }


# =========================================================
# COMPLIANCE ANALYTICS
# =========================================================

def get_compliance_summary(db: Session) -> dict:

    total = (
        db.query(func.count(ContractCompliance.id))
        .scalar()
        or 0
    )

    compliant = _count_by_status(
        db,
        ContractCompliance,
        "Compliant"
    )

    pending = _count_by_status(
        db,
        ContractCompliance,
        "Pending"
    )

    delayed = _count_by_status(
        db,
        ContractCompliance,
        "Delayed"
    )

    non_compliant = _count_by_status(
        db,
        ContractCompliance,
        "Non-Compliant"
    )

    high_risk = (
        db.query(func.count(ContractCompliance.id))
        .filter(
            ContractCompliance.risk_level == "High"
        )
        .scalar()
        or 0
    )

    average_score = (
        db.query(
            func.avg(
                ContractCompliance.compliance_score
            )
        )
        .scalar()
        or 0
    )

    return {
        "total": total,
        "compliant": compliant,
        "pending": pending,
        "delayed": delayed,
        "non_compliant": non_compliant,
        "high_risk": high_risk,
        "average_score": round(
            float(average_score),
            2
        ),
    }


# =========================================================
# RISK ANALYSIS
# =========================================================

def get_risk_analysis(db: Session) -> list:

    contracts = (
        db.query(Contract)
        .all()
    )

    results = []

    for contract in contracts:

        # -------------------------------------------------
        # Count overdue obligations
        # -------------------------------------------------

        overdue_obligations = (
            db.query(func.count(Obligation.id))
            .filter(
                Obligation.contract_id == contract.id,
                Obligation.due_date < date.today(),
                Obligation.status != "Completed",
            )
            .scalar()
            or 0
        )

        # -------------------------------------------------
        # Get latest compliance record
        # -------------------------------------------------

        compliance = (
            db.query(ContractCompliance)
            .filter(
                ContractCompliance.contract_id
                == contract.id
            )
            .order_by(
                ContractCompliance.evaluated_at.desc()
            )
            .first()
        )

        compliance_score = None
        risk_level = "Low"

        if compliance:

            compliance_score = (
                compliance.compliance_score
            )

            risk_level = (
                compliance.risk_level
                or "Low"
            )

        # -------------------------------------------------
        # Calculate risk
        # -------------------------------------------------

        if compliance_score is not None:

            if (
                compliance_score < 60
                or overdue_obligations >= 3
            ):
                risk_level = "High"

            elif (
                compliance_score < 80
                or overdue_obligations > 0
            ):
                risk_level = "Medium"

            else:
                risk_level = "Low"

        elif overdue_obligations >= 3:

            risk_level = "High"

        elif overdue_obligations > 0:

            risk_level = "Medium"

        # -------------------------------------------------
        # Only return contracts requiring attention
        # -------------------------------------------------

        if risk_level in ["High", "Medium"]:

            results.append(
                {
                    "contract_id": contract.id,
                    "contract_number":
                        contract.contract_number,
                    "contract_title":
                        contract.title,
                    "risk_level":
                        risk_level,
                    "overdue_obligations":
                        overdue_obligations,
                    "compliance_score":
                        compliance_score,
                }
            )

    # High risk first

    results.sort(
        key=lambda item: (
            0
            if item["risk_level"] == "High"
            else 1
        )
    )

    return results


# =========================================================
# CONTRACT REPORT
# =========================================================

def get_contract_report(db: Session) -> list:

    contracts = (
        db.query(Contract)
        .all()
    )

    results = []

    for contract in contracts:

        assigned_user_name = None

        if contract.assigned_to:

            user = (
                db.query(User)
                .filter(
                    User.id == contract.assigned_to
                )
                .first()
            )

            if user:
                assigned_user_name = user.full_name

        results.append(
            {
                "contract_number":
                    contract.contract_number,

                "contract_title":
                    contract.title,

                "category":
                    contract.category,

                "status":
                    contract.status,

                "start_date":
                    contract.start_date,

                "end_date":
                    contract.end_date,

                "assigned_user":
                    assigned_user_name,
            }
        )

    return results


# =========================================================
# OBLIGATION REPORT
# =========================================================

def get_obligation_report(db: Session) -> list:

    obligations = (
        db.query(Obligation)
        .all()
    )

    results = []

    for obligation in obligations:

        contract_number = None
        assigned_user_name = None

        if obligation.contract:

            contract_number = (
                obligation.contract.contract_number
            )

        if obligation.assigned_to:

            user = (
                db.query(User)
                .filter(
                    User.id == obligation.assigned_to
                )
                .first()
            )

            if user:
                assigned_user_name = user.full_name

        results.append(
            {
                "contract":
                    contract_number,

                "obligation_title":
                    obligation.title,

                "obligation_type":
                    obligation.obligation_type,

                "assigned_user":
                    assigned_user_name,

                "due_date":
                    obligation.due_date,

                "status":
                    obligation.status,

                "completion_date":
                    obligation.completion_date,
            }
        )

    return results


# =========================================================
# RENEWAL REPORT
# =========================================================

def get_renewal_report(db: Session) -> list:

    renewals = (
        db.query(Renewal)
        .all()
    )

    results = []

    for renewal in renewals:

        contract_number = None
        assigned_user_name = None

        if renewal.contract:

            contract_number = (
                renewal.contract.contract_number
            )

        if renewal.assigned_to:

            user = (
                db.query(User)
                .filter(
                    User.id == renewal.assigned_to
                )
                .first()
            )

            if user:
                assigned_user_name = user.full_name

        results.append(
            {
                "contract":
                    contract_number,

                "previous_expiry_date":
                    renewal.previous_expiry_date,

                "renewal_date":
                    renewal.renewal_date,

                "new_expiry_date":
                    renewal.new_expiry_date,

                "renewal_status":
                    renewal.status,

                "assigned_user":
                    assigned_user_name,
            }
        )

    return results


# =========================================================
# COMPLIANCE REPORT
# =========================================================

def get_compliance_report(db: Session) -> list:

    records = (
        db.query(ContractCompliance)
        .all()
    )

    results = []

    for record in records:

        contract_number = None

        if record.contract:

            contract_number = (
                record.contract.contract_number
            )

        # -------------------------------------------------
        # Count overdue obligations
        # -------------------------------------------------

        overdue_obligations = (
            db.query(func.count(Obligation.id))
            .filter(
                Obligation.contract_id
                == record.contract_id,

                Obligation.due_date
                < date.today(),

                Obligation.status
                != "Completed",
            )
            .scalar()
            or 0
        )

        results.append(
            {
                "contract":
                    contract_number,

                "compliance_status":
                    record.status,

                "compliance_score":
                    record.compliance_score,

                "overdue_obligations":
                    overdue_obligations,

                "risk_level":
                    record.risk_level,

                "evaluation_date":
                    record.evaluated_at,
            }
        )

    return results


# =========================================================
# DASHBOARD SUMMARY
# =========================================================

def get_dashboard_summary(db: Session) -> dict:

    return {
        "contracts":
            get_contract_summary(db),

        "obligations":
            get_obligation_summary(db),

        "renewals":
            get_renewal_summary(db),

        "compliance":
            get_compliance_summary(db),
    }


# =========================================================
# DEPARTMENT PERFORMANCE
# =========================================================

def get_department_performance(
    db: Session
) -> list:

    # Your current User model does not contain
    # a department field.
    #
    # Department analysis is therefore optional.
    #
    # Return an empty list instead of changing
    # the database unnecessarily.

    return []


# =========================================================
# PDF HELPER
# =========================================================

def _create_pdf(
    title: str,
    headers: list,
    rows: list
) -> BytesIO:

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            title,
            styles["Title"]
        )
    )

    elements.append(
        Spacer(1, 12)
    )

    data = [headers]

    for row in rows:

        data.append(
            [
                str(value)
                if value is not None
                else ""
                for value in row
            ]
        )

    table = Table(
        data,
        repeatRows=1
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.grey
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.black
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
            ]
        )
    )

    elements.append(table)

    document.build(elements)

    buffer.seek(0)

    return buffer


# =========================================================
# CONTRACT PDF
# =========================================================

def generate_contract_pdf(
    db: Session
) -> BytesIO:

    report = get_contract_report(db)

    rows = []

    for item in report:

        rows.append(
            [
                item["contract_number"],
                item["contract_title"],
                item["category"],
                item["status"],
                item["start_date"],
                item["end_date"],
                item["assigned_user"],
            ]
        )

    return _create_pdf(
        "ContractIQ - Contract Report",
        [
            "Contract Number",
            "Title",
            "Category",
            "Status",
            "Start Date",
            "End Date",
            "Assigned User",
        ],
        rows,
    )


# =========================================================
# OBLIGATION PDF
# =========================================================

def generate_obligation_pdf(
    db: Session
) -> BytesIO:

    report = get_obligation_report(db)

    rows = []

    for item in report:

        rows.append(
            [
                item["contract"],
                item["obligation_title"],
                item["obligation_type"],
                item["assigned_user"],
                item["due_date"],
                item["status"],
                item["completion_date"],
            ]
        )

    return _create_pdf(
        "ContractIQ - Obligation Report",
        [
            "Contract",
            "Obligation",
            "Type",
            "Assigned User",
            "Due Date",
            "Status",
            "Completion Date",
        ],
        rows,
    )


# =========================================================
# RENEWAL PDF
# =========================================================

def generate_renewal_pdf(
    db: Session
) -> BytesIO:

    report = get_renewal_report(db)

    rows = []

    for item in report:

        rows.append(
            [
                item["contract"],
                item["previous_expiry_date"],
                item["renewal_date"],
                item["new_expiry_date"],
                item["renewal_status"],
                item["assigned_user"],
            ]
        )

    return _create_pdf(
        "ContractIQ - Renewal Report",
        [
            "Contract",
            "Previous Expiry",
            "Renewal Date",
            "New Expiry",
            "Status",
            "Assigned User",
        ],
        rows,
    )


# =========================================================
# COMPLIANCE PDF
# =========================================================

def generate_compliance_pdf(
    db: Session
) -> BytesIO:

    report = get_compliance_report(db)

    rows = []

    for item in report:

        rows.append(
            [
                item["contract"],
                item["compliance_status"],
                item["compliance_score"],
                item["overdue_obligations"],
                item["risk_level"],
                item["evaluation_date"],
            ]
        )

    return _create_pdf(
        "ContractIQ - Compliance Report",
        [
            "Contract",
            "Compliance Status",
            "Score",
            "Overdue Obligations",
            "Risk Level",
            "Evaluation Date",
        ],
        rows,
    )


# =========================================================
# EXCEL HELPER
# =========================================================

def _excel_safe_value(value):
    """
    Convert values into Excel-compatible values.

    Excel/openpyxl does not support timezone-aware
    datetime objects. Therefore, if a datetime contains
    tzinfo, remove the timezone information while
    preserving the date/time value.
    """

    if isinstance(value, datetime):

        if value.tzinfo is not None:

            return value.replace(
                tzinfo=None
            )

        return value

    return value


def _create_excel(
    sheet_name: str,
    headers: list,
    rows: list
) -> BytesIO:

    workbook = Workbook()

    worksheet = workbook.active

    worksheet.title = sheet_name

    # -----------------------------------------------------
    # Header
    # -----------------------------------------------------

    worksheet.append(headers)

    # -----------------------------------------------------
    # Header formatting
    # -----------------------------------------------------

    for cell in worksheet[1]:

        cell.font = Font(
            bold=True
        )

        cell.alignment = Alignment(
            horizontal="center"
        )

    # -----------------------------------------------------
    # Data
    # -----------------------------------------------------

    for row in rows:

        # IMPORTANT:
        # Convert timezone-aware datetime values
        # into timezone-naive values before passing
        # them to openpyxl.

        cleaned_row = [
            _excel_safe_value(value)
            for value in row
        ]

        worksheet.append(cleaned_row)

    # -----------------------------------------------------
    # Adjust column widths
    # -----------------------------------------------------

    for column in worksheet.columns:

        max_length = 0

        column_letter = (
            column[0].column_letter
        )

        for cell in column:

            if cell.value is not None:

                max_length = max(
                    max_length,
                    len(str(cell.value))
                )

        worksheet.column_dimensions[
            column_letter
        ].width = min(
            max_length + 2,
            40
        )

    # -----------------------------------------------------
    # Save workbook
    # -----------------------------------------------------

    buffer = BytesIO()

    workbook.save(buffer)

    buffer.seek(0)

    return buffer


# =========================================================
# CONTRACT EXCEL
# =========================================================

def generate_contract_excel(
    db: Session
) -> BytesIO:

    report = get_contract_report(db)

    rows = []

    for item in report:

        rows.append(
            [
                item["contract_number"],
                item["contract_title"],
                item["category"],
                item["status"],
                item["start_date"],
                item["end_date"],
                item["assigned_user"],
            ]
        )

    return _create_excel(
        "Contracts",
        [
            "Contract Number",
            "Title",
            "Category",
            "Status",
            "Start Date",
            "End Date",
            "Assigned User",
        ],
        rows,
    )


# =========================================================
# OBLIGATION EXCEL
# =========================================================

def generate_obligation_excel(
    db: Session
) -> BytesIO:

    report = get_obligation_report(db)

    rows = []

    for item in report:

        rows.append(
            [
                item["contract"],
                item["obligation_title"],
                item["obligation_type"],
                item["assigned_user"],
                item["due_date"],
                item["status"],
                item["completion_date"],
            ]
        )

    return _create_excel(
        "Obligations",
        [
            "Contract",
            "Obligation",
            "Type",
            "Assigned User",
            "Due Date",
            "Status",
            "Completion Date",
        ],
        rows,
    )


# =========================================================
# RENEWAL EXCEL
# =========================================================

def generate_renewal_excel(
    db: Session
) -> BytesIO:

    report = get_renewal_report(db)

    rows = []

    for item in report:

        rows.append(
            [
                item["contract"],
                item["previous_expiry_date"],
                item["renewal_date"],
                item["new_expiry_date"],
                item["renewal_status"],
                item["assigned_user"],
            ]
        )

    return _create_excel(
        "Renewals",
        [
            "Contract",
            "Previous Expiry",
            "Renewal Date",
            "New Expiry",
            "Status",
            "Assigned User",
        ],
        rows,
    )


# =========================================================
# COMPLIANCE EXCEL
# =========================================================

def generate_compliance_excel(
    db: Session
) -> BytesIO:

    report = get_compliance_report(db)

    rows = []

    for item in report:

        rows.append(
            [
                item["contract"],
                item["compliance_status"],
                item["compliance_score"],
                item["overdue_obligations"],
                item["risk_level"],
                item["evaluation_date"],
            ]
        )

    return _create_excel(
        "Compliance",
        [
            "Contract",
            "Compliance Status",
            "Score",
            "Overdue Obligations",
            "Risk Level",
            "Evaluation Date",
        ],
        rows,
    )