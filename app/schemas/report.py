# app/schemas/report.py

from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict


# =========================================================
# EXISTING REPORT CRUD SCHEMAS
# =========================================================

class ReportCreate(BaseModel):
    name: str
    report_type: str
    generated_by: int
    file_path: str | None = None
    format: str


class ReportResponse(BaseModel):
    id: int
    name: str
    report_type: str
    generated_by: int
    file_path: str | None
    format: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# CONTRACT ANALYTICS
# =========================================================

class ContractStatistics(BaseModel):
    total: int
    active: int
    draft: int
    under_review: int
    approved: int
    expired: int
    terminated: int
    by_category: Dict[str, int]


# =========================================================
# OBLIGATION ANALYTICS
# =========================================================

class ObligationStatistics(BaseModel):
    total: int
    pending: int
    in_progress: int
    completed: int
    delayed: int
    overdue: int


# =========================================================
# RENEWAL ANALYTICS
# =========================================================

class UpcomingRenewal(BaseModel):
    contract_id: int
    contract_number: Optional[str] = None
    contract_title: Optional[str] = None
    expiry_date: Optional[date] = None
    days_remaining: Optional[int] = None


class RenewalStatistics(BaseModel):
    upcoming: int
    in_progress: int
    renewed: int
    expired: int
    cancelled: int
    approaching_expiry: List[UpcomingRenewal]


# =========================================================
# COMPLIANCE ANALYTICS
# =========================================================

class ComplianceStatistics(BaseModel):
    total: int
    compliant: int
    pending: int
    delayed: int
    non_compliant: int
    high_risk: int
    average_score: float


# =========================================================
# RISK ANALYSIS
# =========================================================

class RiskItem(BaseModel):
    contract_id: int
    contract_number: Optional[str] = None
    contract_title: Optional[str] = None
    risk_level: str
    overdue_obligations: int
    compliance_score: Optional[float] = None


# =========================================================
# DASHBOARD SUMMARY
# =========================================================

class DashboardSummary(BaseModel):
    contracts: ContractStatistics
    obligations: ObligationStatistics
    renewals: RenewalStatistics
    compliance: ComplianceStatistics


# =========================================================
# DEPARTMENT PERFORMANCE
# =========================================================

class DepartmentPerformance(BaseModel):
    department: str
    contracts: int
    obligations: int
    overdue: int