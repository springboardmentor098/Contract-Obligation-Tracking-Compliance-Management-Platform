from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ============================================================
# Contract Reports
# ============================================================

class ContractSummaryResponse(BaseModel):
    total_contracts: int
    active_contracts: int
    expired_contracts: int
    pending_approval_contracts: int
    contracts_by_status: Dict[str, int]


# ============================================================
# Obligation Reports
# ============================================================

class ObligationSummaryResponse(BaseModel):
    total_obligations: int
    pending_obligations: int
    completed_obligations: int
    overdue_obligations: int
    obligations_by_status: Dict[str, int]


# ============================================================
# Renewal Reports
# ============================================================

class UpcomingRenewalResponse(BaseModel):
    renewal_id: int
    contract_id: int
    contract_title: str
    contract_number: str
    previous_expiry_date: str
    renewal_date: Optional[str] = None
    new_expiry_date: Optional[str] = None
    status: str


class RenewalSummaryResponse(BaseModel):
    upcoming_renewals: List[UpcomingRenewalResponse]
    expired_contracts: int
    immediate_attention: List[UpcomingRenewalResponse]


# ============================================================
# Compliance Reports
# ============================================================

class ComplianceSummaryResponse(BaseModel):
    total_contracts: int
    compliant_contracts: int
    non_compliant_contracts: int
    high_risk_obligations: int
    compliance_percentage: float


# ============================================================
# Dashboard
# ============================================================

class DashboardSummaryResponse(BaseModel):
    contracts: ContractSummaryResponse
    obligations: ObligationSummaryResponse
    renewals: RenewalSummaryResponse
    compliance: ComplianceSummaryResponse
