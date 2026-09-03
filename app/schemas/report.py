from datetime import date, datetime
from pydantic import BaseModel


# -----------------------------
# Dashboard Summary
# -----------------------------

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


# -----------------------------
# Contract Report
# -----------------------------

class ContractSummaryResponse(BaseModel):
    total_contracts: int
    active_contracts: int
    draft_contracts: int
    under_review_contracts: int
    approved_contracts: int
    expired_contracts: int
    terminated_contracts: int
    contracts_by_category: dict[str, int]


# -----------------------------
# Obligation Report
# -----------------------------

class ObligationSummaryResponse(BaseModel):
    total_obligations: int
    pending_obligations: int
    in_progress_obligations: int
    completed_obligations: int
    delayed_obligations: int
    overdue_obligations: int


# -----------------------------
# Renewal Report
# -----------------------------

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


# -----------------------------
# Compliance Report
# -----------------------------

class ComplianceSummaryResponse(BaseModel):
    total_contracts: int
    compliant: int
    pending: int
    delayed: int
    non_compliant: int
    high_risk: int
    average_score: float


# -----------------------------
# Risk Analysis
# -----------------------------

class RiskSummary(BaseModel):
    contract_id: int
    contract_number: str
    risk_level: str
    overdue_obligations: int
    compliance_score: float


# -----------------------------
# Department Performance
# -----------------------------

class DepartmentPerformance(BaseModel):
    department: str
    contracts: int
    obligations: int
    overdue: int