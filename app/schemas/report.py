from datetime import date

from pydantic import BaseModel, Field


class ContractStatistics(BaseModel):
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
    expiry_date: date
    days_remaining: int


class RenewalStatistics(BaseModel):
    upcoming: int
    in_progress: int
    renewed: int
    expired: int
    cancelled: int
    approaching_expiry: list[UpcomingRenewal]


class ComplianceStatistics(BaseModel):
    total_contracts: int
    compliant: int
    pending: int
    delayed: int
    non_compliant: int
    high_risk: int
    average_score: float = Field(ge=0, le=100)


class DashboardSummary(BaseModel):
    contracts: ContractStatistics
    obligations: ObligationStatistics
    renewals: RenewalStatistics
    compliance: ComplianceStatistics


class RiskSummary(BaseModel):
    contract_id: int
    contract_number: str
    contract_title: str
    risk_level: str
    overdue_obligations: int
    compliance_score: float = Field(ge=0, le=100)


class DepartmentPerformance(BaseModel):
    available: bool
    limitation: str | None = None
    departments: list[dict[str, object]] = Field(default_factory=list)