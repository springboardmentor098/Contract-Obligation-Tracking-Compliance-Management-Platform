from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class StatusCount(BaseModel):
    status: str
    count: int


# ============================================================
# CONTRACT REPORTS
# ============================================================

class ContractSummaryResponse(BaseModel):
    total_contracts: int
    active_contracts: int
    expired_contracts: int
    pending_approval: int


class ContractStatusDistributionResponse(BaseModel):
    data: list[StatusCount]


# ============================================================
# OBLIGATION REPORTS
# ============================================================

class ObligationSummaryResponse(BaseModel):
    total_obligations: int
    pending_obligations: int
    completed_obligations: int
    overdue_obligations: int


class ObligationStatusDistributionResponse(BaseModel):
    data: list[StatusCount]


# ============================================================
# RENEWAL REPORTS
# ============================================================

class RenewalReportItem(BaseModel):
    id: UUID
    contract_id: UUID
    renewal_date: date | None
    previous_expiry_date: date | None
    new_expiry_date: date | None
    status: str

    model_config = ConfigDict(from_attributes=True)


class RenewalSummaryResponse(BaseModel):
    upcoming_renewals: list[RenewalReportItem]
    expired_contracts: int
    contracts_requiring_attention: int


# ============================================================
# COMPLIANCE REPORTS
# ============================================================

class ComplianceSummaryResponse(BaseModel):
    total_contracts: int
    compliant_contracts: int
    non_compliant_contracts: int
    high_risk_contracts: int
    high_risk_obligations: int
    average_compliance_score: float


# ============================================================
# DASHBOARD
# ============================================================

class DashboardResponse(BaseModel):
    contracts: ContractSummaryResponse
    contract_status_distribution: list[StatusCount]

    obligations: ObligationSummaryResponse
    obligation_status_distribution: list[StatusCount]

    renewals: RenewalSummaryResponse

    compliance: ComplianceSummaryResponse