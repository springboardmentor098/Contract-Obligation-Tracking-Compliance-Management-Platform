from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReportCreate(BaseModel):
    user_id: int
    contract_id: int | None = None

    report_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    file_path: str | None = Field(
        default=None,
        max_length=500,
    )


class ReportUpdate(BaseModel):
    report_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    file_path: str | None = Field(
        default=None,
        max_length=500,
    )


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    contract_id: int | None
    report_type: str
    title: str
    description: str | None
    file_path: str | None
    generated_at: datetime

class ContractDashboardSummary(BaseModel):
    total: int
    active: int
    draft: int
    under_review: int
    expired: int


class ObligationDashboardSummary(BaseModel):
    total: int
    pending: int
    overdue: int
    completed: int


class RenewalDashboardSummary(BaseModel):
    total: int
    upcoming: int
    completed: int


class ComplianceDashboardSummary(BaseModel):
    compliant_contracts: int
    non_compliant_contracts: int
    high_risk_contracts: int


class DashboardSummary(BaseModel):
    contracts: ContractDashboardSummary
    obligations: ObligationDashboardSummary
    renewals: RenewalDashboardSummary
    compliance: ComplianceDashboardSummary

class ContractAnalyticsSummary(BaseModel):
    total: int
    by_status: dict[str, int]
    by_category: dict[str, int]
    by_counterparty: dict[str, int]
    expiring_next_30_days: int
    expiring_next_90_days: int


class ContractAnalyticsResponse(BaseModel):
    contracts: ContractAnalyticsSummary

class ObligationAnalyticsSummary(BaseModel):
    total: int
    by_status: dict[str, int]
    by_priority: dict[str, int]
    by_responsible_party: dict[str, int]
    overdue: int
    due_next_7_days: int
    due_next_30_days: int


class ObligationAnalyticsResponse(BaseModel):
    obligations: ObligationAnalyticsSummary

class RenewalAnalyticsSummary(BaseModel):
    total: int
    by_status: dict[str, int]
    due_next_7_days: int
    due_next_30_days: int
    due_next_90_days: int
    overdue: int
    by_contract: dict[str, int]


class RenewalAnalyticsResponse(BaseModel):
    renewals: RenewalAnalyticsSummary

class ComplianceAnalyticsSummary(BaseModel):
    total_contracts: int
    compliant_contracts: int
    non_compliant_contracts: int
    high_risk_contracts: int
    compliance_rate: float
    overdue_obligations: int
    high_priority_overdue_obligations: int


class ComplianceAnalyticsResponse(BaseModel):
    compliance: ComplianceAnalyticsSummary
