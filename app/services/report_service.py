import io
import pandas as pd
from fpdf import FPDF
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.all_models import Contract, Obligation, Renewal, ComplianceRecord, ObligationStatus, RenewalStatus, ComplianceStatusEnum, RiskLevelEnum

# ==========================================
# 📊 FAST DATABASE AGGREGATIONS
# ==========================================

def get_dashboard_summary(db: Session):
    # Contracts Math
    total_contracts = db.query(Contract).count()
    active_contracts = db.query(Contract).filter(Contract.status == "Active").count()
    draft_contracts = db.query(Contract).filter(Contract.status == "Draft").count()
    
    # Obligations Math
    total_obligations = db.query(Obligation).count()
    pending_obs = db.query(Obligation).filter(Obligation.status == ObligationStatus.PENDING).count()
    in_prog_obs = db.query(Obligation).filter(Obligation.status == ObligationStatus.IN_PROGRESS).count()
    completed_obs = db.query(Obligation).filter(Obligation.status == ObligationStatus.COMPLETED).count()
    overdue_obs = db.query(Obligation).filter(Obligation.status == ObligationStatus.OVERDUE).count()
    
    # Renewals Math
    upcoming_ren = db.query(Renewal).filter(Renewal.status == RenewalStatus.UPCOMING).count()
    expired_ren = db.query(Renewal).filter(Renewal.status == RenewalStatus.EXPIRED).count()
    
    # Compliance Math (checking the most recent evaluations)
    comp_compliant = db.query(ComplianceRecord).filter(ComplianceRecord.status == ComplianceStatusEnum.COMPLIANT).count()
    comp_non_compliant = db.query(ComplianceRecord).filter(ComplianceRecord.status == ComplianceStatusEnum.NON_COMPLIANT).count()
    comp_high_risk = db.query(ComplianceRecord).filter(ComplianceRecord.status == ComplianceStatusEnum.HIGH_RISK).count()

    return {
        "contracts": {
            "total": total_contracts,
            "active": active_contracts,
            "draft": draft_contracts
        },
        "obligations": {
            "total": total_obligations,
            "pending": pending_obs,
            "in_progress": in_prog_obs,
            "completed": completed_obs,
            "overdue": overdue_obs
        },
        "renewals": {
            "upcoming": upcoming_ren,
            "expired": expired_ren
        },
        "compliance": {
            "compliant": comp_compliant,
            "non_compliant": comp_non_compliant,
            "high_risk": comp_high_risk
        }
    }

# ==========================================
# 📄 FILE EXPORT LOGIC
# ==========================================

def generate_excel_report(data: list, columns: list):
    """Generates an Excel file in-memory using pandas."""
    df = pd.DataFrame(data, columns=columns)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Report Data')
    output.seek(0)
    return output

def generate_pdf_report(title: str, data: list, columns: list):
    """Generates a simple PDF file in-memory using fpdf2."""
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(10)
    
    # Table Header
    pdf.set_font("helvetica", "B", 10)
    col_width = 190 / len(columns)
    for col in columns:
        pdf.cell(col_width, 10, col, border=1, align="C")
    pdf.ln()
    
    # Table Rows
    pdf.set_font("helvetica", "", 9)
    for row in data:
        for item in row:
            # Truncate text to fit the cell
            text = str(item)[:20] if item else "N/A"
            pdf.cell(col_width, 10, text, border=1, align="C")
        pdf.ln()
        
    return io.BytesIO(pdf.output())