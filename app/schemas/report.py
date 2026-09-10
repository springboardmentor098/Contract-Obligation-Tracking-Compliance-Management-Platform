from datetime import date
from typing import Optional

from pydantic import BaseModel


# ============================================================
# CONTRACT REPORT
# ============================================================

class ContractStatusCount(BaseModel):
    status: str
    count: int


class ContractSummaryResponse(BaseModel):
    total_contracts: int
    active_contracts: int
    expired_contracts: int
    pending_approval: int
    contracts_by_status: list[ContractStatusCount]


# ============================================================
# OBLIGATION REPORT
# ============================================================

class ObligationStatusCount(BaseModel):
    status: str
    count: int


class ObligationSummaryResponse(BaseModel):
    total_obligations: int
    pending_obligations: int
    completed_obligations: int
    overdue_obligations: int
    obligations_by_status: list[ObligationStatusCount]


# ============================================================
# RENEWAL REPORT
# ============================================================

class RenewalItem(BaseModel):
    renewal_id: int
    contract_id: int
    renewal_date: Optional[date]
    contract_end_date: date
    status: str


class RenewalSummaryResponse(BaseModel):
    upcoming_renewals: int
    expired_contracts: int
    immediate_attention: int
    renewals: list[RenewalItem]


# ============================================================
# COMPLIANCE REPORT
# ============================================================

class ComplianceSummaryResponse(BaseModel):
    total_contracts: int
    compliant_contracts: int
    partially_compliant_contracts: int
    non_compliant_contracts: int
    high_risk_contracts: int
    high_risk_obligations: int
    overall_compliance_percentage: float


# ============================================================
# DASHBOARD REPORT
# ============================================================

class DashboardResponse(BaseModel):
    contracts: ContractSummaryResponse
    obligations: ObligationSummaryResponse
    renewals: RenewalSummaryResponse
    compliance: ComplianceSummaryResponse