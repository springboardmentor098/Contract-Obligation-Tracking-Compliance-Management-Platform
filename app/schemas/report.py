from datetime import date

from pydantic import BaseModel


# =========================================================
# DASHBOARD SUMMARY
# =========================================================

class ContractStatistics(BaseModel):
    total: int
    active: int
    draft: int
    under_review: int
    approved: int
    expired: int
    terminated: int


class ObligationStatistics(BaseModel):
    total: int
    pending: int
    in_progress: int
    completed: int
    delayed: int
    overdue: int


class RenewalStatistics(BaseModel):
    upcoming: int
    in_progress: int
    renewed: int
    expired: int
    cancelled: int


class ComplianceStatistics(BaseModel):
    total: int
    compliant: int
    pending: int
    delayed: int
    non_compliant: int
    high_risk: int
    average_score: float


class DashboardSummaryResponse(BaseModel):
    contracts: ContractStatistics
    obligations: ObligationStatistics
    renewals: RenewalStatistics
    compliance: ComplianceStatistics


# =========================================================
# CONTRACT SUMMARY
# =========================================================

class ContractSummaryResponse(BaseModel):
    total_contracts: int
    active_contracts: int
    expired_contracts: int
    pending_approval_contracts: int
    contracts_by_status: dict[str, int]
    contracts_by_category: dict[str, int]


# =========================================================
# OBLIGATION SUMMARY
# =========================================================

class ObligationSummaryResponse(BaseModel):
    total_obligations: int
    pending_obligations: int
    completed_obligations: int
    overdue_obligations: int
    in_progress_obligations: int
    delayed_obligations: int
    obligations_by_status: dict[str, int]


# =========================================================
# RENEWAL SUMMARY
# =========================================================

class UpcomingRenewal(BaseModel):
    contract_id: int
    contract_number: str
    expiry_date: date
    days_remaining: int


class RenewalSummaryResponse(BaseModel):
    upcoming: int
    in_progress: int
    renewed: int
    expired: int
    cancelled: int
    upcoming_contracts: list[UpcomingRenewal]
    immediate_attention: list[UpcomingRenewal]
    renewals_in_date_range: int


# =========================================================
# COMPLIANCE SUMMARY
# =========================================================

class ComplianceSummaryResponse(BaseModel):
    total_contracts: int
    compliant: int
    pending: int
    delayed: int
    non_compliant: int
    high_risk: int
    average_score: float


# =========================================================
# RISK SUMMARY
# =========================================================

class RiskSummary(BaseModel):
    contract_id: int
    contract_number: str
    risk_level: str
    overdue_obligations: int
    compliance_score: float


# =========================================================
# DEPARTMENT PERFORMANCE
# =========================================================

class DepartmentPerformance(BaseModel):
    department: str
    contracts: int
    obligations: int
    overdue: int