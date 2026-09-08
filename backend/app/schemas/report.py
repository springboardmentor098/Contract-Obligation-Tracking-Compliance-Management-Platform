from pydantic import BaseModel
from typing import Dict



# ============================================================
# CONTRACT SUMMARY
# ============================================================

class ContractSummary(BaseModel):

    total: int
    active: int
    draft: int
    under_review: int
    approved: int
    expired: int
    terminated: int
    categories: Dict[str, int] = {}


# ============================================================
# OBLIGATION SUMMARY
# ============================================================

class ObligationSummary(BaseModel):

    total: int
    pending: int
    in_progress: int
    completed: int
    delayed: int
    overdue: int


# ============================================================
# RENEWAL SUMMARY
# ============================================================

class RenewalSummary(BaseModel):

    upcoming: int
    in_progress: int
    renewed: int
    expired: int
    cancelled: int


# ============================================================
# COMPLIANCE SUMMARY
# ============================================================

class ComplianceReportSummary(BaseModel):

    total_contracts: int
    compliant: int
    pending: int
    delayed: int
    non_compliant: int
    high_risk: int
    average_compliance_score: float
class DashboardComplianceSummary(BaseModel):

    compliant: int
    pending: int
    delayed: int
    non_compliant: int
    high_risk: int


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

class DashboardSummary(BaseModel):

    contracts: ContractSummary
    obligations: ObligationSummary
    renewals: RenewalSummary
    compliance: DashboardComplianceSummary

# ============================================================
# RISK REPORT
# ============================================================

class RiskReport(BaseModel):

    contract_id: int
    contract_number: str | None = None
    risk_level: str
    overdue_obligations: int
    compliance_score: float
# ============================================================
# DEPARTMENT PERFORMANCE
# ============================================================

class DepartmentPerformance(BaseModel):

    department: str
    contracts: int
    obligations: int
    overdue: int
    