import io
import traceback
from typing import List

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.all_models import Contract, Obligation, Renewal, ComplianceRecord, ObligationStatus, ComplianceStatusEnum
from app.models.contract import ContractStatus
from app.schemas.report import DashboardSummaryResponse, RiskReportResponse, GenericSummaryResponse
from app.core.security import get_current_user
from app.services.report_service import get_dashboard_summary

router = APIRouter(tags=["Reports & Analytics"])


def _empty_summary():
    return {
        "total_contracts": 0,
        "contracts_by_status": {
            "Active": 0,
            "Draft": 0,
            "Expired": 0,
        },
        "total_obligations": 0,
        "overdue_obligations": 0,
    }


@router.get("/reports/summary", status_code=status.HTTP_200_OK)
def get_reports_summary(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        total_contracts = db.query(Contract).count()
        active_contracts = db.query(Contract).filter(Contract.status == ContractStatus.ACTIVE).count()
        draft_contracts = db.query(Contract).filter(Contract.status == ContractStatus.DRAFT).count()
        expired_contracts = db.query(Contract).filter(Contract.status == ContractStatus.EXPIRED).count()
        total_obligations = db.query(Obligation).count()
        overdue_obligations = db.query(Obligation).filter(Obligation.status == ObligationStatus.OVERDUE).count()

        return {
            "total_contracts": total_contracts,
            "contracts_by_status": {
                "Active": active_contracts,
                "Draft": draft_contracts,
                "Expired": expired_contracts,
            },
            "total_obligations": total_obligations,
            "overdue_obligations": overdue_obligations,
        }
    except Exception as exc:
        print(f"ERROR get_reports_summary: {exc}")
        traceback.print_exc()
        return _empty_summary()


# Helper to safely format status keys (handles both Enums and Strings)
def format_status(status_val):
    return status_val.value if hasattr(status_val, 'value') else str(status_val)


# 1. API: Dashboard Summary
@router.get("/dashboard/summary", response_model=DashboardSummaryResponse, status_code=status.HTTP_200_OK)
def get_dashboard(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return get_dashboard_summary(db)


# 2. API: Contract Analytics
@router.get("/reports/contracts/summary", response_model=GenericSummaryResponse, status_code=status.HTTP_200_OK)
def get_contract_summary(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    total = db.query(Contract).count()
    status_counts = db.query(Contract.status, func.count(Contract.id)).group_by(Contract.status).all()
    breakdown = {format_status(s): c for s, c in status_counts if s}
    return {"total": total, "breakdown": breakdown}


# 3. API: Obligation Analytics
@router.get("/reports/obligations/summary", response_model=GenericSummaryResponse, status_code=status.HTTP_200_OK)
def get_obligation_summary(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    total = db.query(Obligation).count()
    status_counts = db.query(Obligation.status, func.count(Obligation.id)).group_by(Obligation.status).all()
    breakdown = {format_status(s): c for s, c in status_counts if s}
    return {"total": total, "breakdown": breakdown}


# 4. API: Renewal Analytics
@router.get("/reports/renewals/summary", response_model=GenericSummaryResponse, status_code=status.HTTP_200_OK)
def get_renewal_summary(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    total = db.query(Renewal).count()
    status_counts = db.query(Renewal.status, func.count(Renewal.id)).group_by(Renewal.status).all()
    breakdown = {format_status(s): c for s, c in status_counts if s}
    return {"total": total, "breakdown": breakdown}


# 5. API: Compliance Analytics
@router.get("/reports/compliance/summary", response_model=GenericSummaryResponse, status_code=status.HTTP_200_OK)
def get_compliance_summary(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    total = db.query(ComplianceRecord).count()
    status_counts = db.query(ComplianceRecord.status, func.count(ComplianceRecord.id)).group_by(ComplianceRecord.status).all()
    breakdown = {format_status(s): c for s, c in status_counts if s}
    return {"total": total, "breakdown": breakdown}


# 6. API: Risk Analysis
@router.get("/reports/risk", response_model=List[RiskReportResponse], status_code=status.HTTP_200_OK)
def get_risk_report(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    high_risk = db.query(ComplianceRecord).filter(ComplianceRecord.status == ComplianceStatusEnum.HIGH_RISK).all()
    results = []
    for record in high_risk:
        contract = record.contract
        results.append({
            "contract_id": contract.id,
            "contract_number": getattr(contract, 'contract_number', f"CNT-{contract.id}"),
            "risk_level": record.risk_level.value,
            "overdue_obligations": sum(1 for o in contract.obligations if o.status == ObligationStatus.OVERDUE),
            "compliance_score": record.compliance_score
        })
    return results


def _build_excel_response(rows: list, filename: str):
    buffer = io.BytesIO()
    df = pd.DataFrame(rows, columns=["Type", "Title", "Status", "Start/Due Date", "End Date"])
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="ContractIQ Report")
    buffer.seek(0)
    return StreamingResponse(iter([buffer.getvalue()]), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


def _build_pdf_response(title: str, rows: list, filename: str):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(title)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(72, 750, title)
    pdf.setFont("Helvetica", 10)
    y = 720
    for row in rows[:20]:
        pdf.drawString(72, y, " | ".join(str(item) for item in row))
        y -= 16
        if y < 60:
            pdf.showPage()
            y = 750
    pdf.save()
    buffer.seek(0)
    return StreamingResponse(iter([buffer.getvalue()]), media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


# 7. API: Export Excel Report
@router.get("/reports/export/excel")
def export_contracts_excel(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        contracts = db.query(Contract).all()
        obligations = db.query(Obligation).all()
        export_rows = [
            ["Contract", c.title, str(c.status), str(c.start_date), str(c.end_date)] for c in contracts
        ] + [
            ["Obligation", o.title, str(o.status), str(o.due_date), ""] for o in obligations
        ]
        return _build_excel_response(export_rows, "contractiq_report.xlsx")
    except Exception as exc:
        print(f"ERROR export_contracts_excel: {exc}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to generate Excel report.")


# 8. API: Export PDF Report
@router.get("/reports/export/pdf")
def export_contracts_pdf(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        contracts = db.query(Contract).all()
        obligations = db.query(Obligation).all()
        data = [
            ["Contract", c.title, str(c.status), str(c.end_date)] for c in contracts
        ] + [
            ["Obligation", o.title, str(o.status), str(o.due_date)] for o in obligations
        ]
        return _build_pdf_response("ContractIQ Overview Report", data, "contractiq_report.pdf")
    except Exception as exc:
        print(f"ERROR export_contracts_pdf: {exc}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to generate PDF report.")


@router.get("/reports/contracts/export/excel")
def export_contracts_excel_legacy(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return export_contracts_excel(db=db, current_user=current_user)


@router.get("/reports/contracts/export/pdf")
def export_contracts_pdf_legacy(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return export_contracts_pdf(db=db, current_user=current_user)