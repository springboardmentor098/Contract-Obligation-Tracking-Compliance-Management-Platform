from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database.database import get_db
from app.models.all_models import Contract, Obligation, Renewal, ComplianceRecord, ObligationStatus, ComplianceStatusEnum
from app.schemas.report import DashboardSummaryResponse, RiskReportResponse, GenericSummaryResponse
from app.core.security import get_current_user
from app.services.report_service import get_dashboard_summary, generate_excel_report, generate_pdf_report

router = APIRouter(tags=["Reports & Analytics"])

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

# 7. API: Export Excel Report
@router.get("/reports/contracts/export/excel")
def export_contracts_excel(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    contracts = db.query(Contract).all()
    columns = ["ID", "Title", "Status", "Start Date", "End Date"]
    data = [[c.id, c.title, c.status, c.start_date, c.end_date] for c in contracts]
    
    excel_file = generate_excel_report(data, columns)
    
    return StreamingResponse(
        excel_file, 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
        headers={"Content-Disposition": "attachment; filename=contracts_report.xlsx"}
    )

# 8. API: Export PDF Report
@router.get("/reports/contracts/export/pdf")
def export_contracts_pdf(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    contracts = db.query(Contract).all()
    columns = ["ID", "Title", "Status", "End Date"]
    data = [[str(c.id), c.title, c.status, str(c.end_date)] for c in contracts]
    
    pdf_file = generate_pdf_report("Contracts Overview Report", data, columns)
    
    return StreamingResponse(
        pdf_file, 
        media_type="application/pdf", 
        headers={"Content-Disposition": "attachment; filename=contracts_report.pdf"}
    )