from pydantic import BaseModel
from typing import List


class ContractStatusStatistics(BaseModel):
    total: int
    active: int
    draft: int
    under_review: int
    approved: int
    expired: int
    terminated: int
    by_category: dict[str, int]


class ObligationStatistics(BaseModel):
    total: int
    pending: int
    in_progress: int
    completed: int
    delayed: int
    overdue: int


class UpcomingRenewal(BaseModel):
    contract_id: int
    contract_number: str
    contract_title: str
    expiry_date: str
    days_remaining: int


class RenewalStatistics(BaseModel):
    upcoming: int
    in_progress: int
    renewed: int
    expired: int
    cancelled: int
    upcoming_contracts: List[UpcomingRenewal]


class ComplianceStatistics(BaseModel):
    total_contracts: int
    compliant: int
    pending: int
    delayed: int
    non_compliant: int
    high_risk: int
    average_score: float


class RiskSummary(BaseModel):
    contract_id: int
    contract_number: str
    risk_level: str
    overdue_obligations: int
    compliance_score: float


class DepartmentPerformance(BaseModel):
    department: str
    contracts: int
    obligations: int
    overdue: int


class DashboardSummary(BaseModel):
    contracts: ContractStatusStatistics
    obligations: ObligationStatistics
    renewals: RenewalStatistics
    compliance: ComplianceStatistics
