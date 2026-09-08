from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel


# =========================================================
# CONTRACT ANALYTICS
# =========================================================

class ContractSummaryResponse(BaseModel):
    total: int
    active: int
    draft: int
    under_review: int
    approved: int
    expired: int
    terminated: int
    contracts_by_category: Dict[str, int]


# =========================================================
# OBLIGATION ANALYTICS
# =========================================================

class ObligationSummaryResponse(BaseModel):
    total: int
    pending: int
    in_progress: int
    completed: int
    delayed: int
    overdue: int


# =========================================================
# RENEWAL ANALYTICS
# =========================================================

class ApproachingExpiryResponse(BaseModel):
    contract_id: int
    contract_number: str
    title: str
    expiry_date: date
    days_remaining: int


class RenewalSummaryResponse(BaseModel):
    upcoming: int
    in_progress: int
    renewed: int
    expired: int
    cancelled: int
    approaching_expiry: List[ApproachingExpiryResponse]


# =========================================================
# COMPLIANCE ANALYTICS
# =========================================================

class ComplianceSummaryResponse(BaseModel):
    total_evaluated: int
    compliant: int
    pending: int
    delayed: int
    non_compliant: int
    high_risk: int
    average_score: float


# =========================================================
# RISK ANALYTICS
# =========================================================

class RiskContractResponse(BaseModel):
    contract_id: int
    contract_number: str
    risk_level: str
    overdue_obligations: int
    compliance_score: float


class RiskSummaryResponse(BaseModel):
    total_at_risk: int
    contracts: List[RiskContractResponse]


# =========================================================
# DASHBOARD SUMMARY
# =========================================================

class DashboardContractSummary(BaseModel):
    total: int
    active: int
    draft: int
    under_review: int
    approved: int
    expired: int
    terminated: int


class DashboardObligationSummary(BaseModel):
    total: int
    pending: int
    in_progress: int
    completed: int
    overdue: int


class DashboardRenewalSummary(BaseModel):
    upcoming: int
    in_progress: int
    renewed: int
    expired: int


class DashboardComplianceSummary(BaseModel):
    compliant: int
    pending: int
    delayed: int
    non_compliant: int
    high_risk: int


class DashboardSummaryResponse(BaseModel):
    contracts: DashboardContractSummary
    obligations: DashboardObligationSummary
    renewals: DashboardRenewalSummary
    compliance: DashboardComplianceSummary


# =========================================================
# DEPARTMENT PERFORMANCE
# =========================================================

class DepartmentPerformanceResponse(BaseModel):
    message: str
    available: bool


# =========================================================
# CONTRACT REPORT
# =========================================================

class ContractReportItem(BaseModel):
    contract_number: str
    title: str
    category: str
    status: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    assigned_user: Optional[str] = None


class ContractReportResponse(BaseModel):
    report_type: str
    total_records: int
    data: List[ContractReportItem]


# =========================================================
# OBLIGATION REPORT
# =========================================================

class ObligationReportItem(BaseModel):
    contract_number: str
    title: str
    obligation_type: str
    assigned_user: Optional[str] = None
    due_date: Optional[date] = None
    status: str
    completion_date: Optional[date] = None


class ObligationReportResponse(BaseModel):
    report_type: str
    total_records: int
    data: List[ObligationReportItem]


# =========================================================
# RENEWAL REPORT
# =========================================================

class RenewalReportItem(BaseModel):
    contract_number: str
    previous_expiry_date: Optional[date] = None
    renewal_date: Optional[date] = None
    new_expiry_date: Optional[date] = None
    status: str
    assigned_user: Optional[str] = None


class RenewalReportResponse(BaseModel):
    report_type: str
    total_records: int
    data: List[RenewalReportItem]


# =========================================================
# COMPLIANCE REPORT
# =========================================================

class ComplianceReportItem(BaseModel):
    contract_number: str
    compliance_status: str
    compliance_score: float
    overdue_obligations: int
    risk_level: str
    evaluation_date: date


class ComplianceReportResponse(BaseModel):
    report_type: str
    total_records: int
    data: List[ComplianceReportItem]