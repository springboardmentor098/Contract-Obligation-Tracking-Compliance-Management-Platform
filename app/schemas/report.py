from typing import Dict, List, Optional
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_contracts: int
    active_contracts: int
    draft_contracts: int
    contracts_under_review: int
    upcoming_renewals: int
    expired_contracts: int
    total_obligations: int
    pending_obligations: int
    overdue_obligations: int
    completed_obligations: int
    compliant_contracts: int
    non_compliant_contracts: int
    high_risk_contracts: int


class ContractStats(BaseModel):
    total: int
    active: int
    draft: int
    under_review: int
    approved: int
    expired: int
    terminated: int
    by_category: Dict[str, int]


class ObligationStats(BaseModel):
    total: int
    pending: int
    in_progress: int
    completed: int
    delayed: int
    overdue: int


class RenewalItem(BaseModel):
    contract_id: int
    contract_number: str
    expiry_date: str
    days_remaining: int


class RenewalStats(BaseModel):
    upcoming: int
    in_progress: int
    renewed: int
    expired: int
    cancelled: int
    approaching_expiry: List[RenewalItem]


class ComplianceStats(BaseModel):
    total_evaluated: int
    compliant: int
    pending: int
    delayed: int
    non_compliant: int
    high_risk: int
    average_compliance_score: Optional[float]


class RiskItem(BaseModel):
    contract_id: int
    contract_number: str
    risk_level: str
    overdue_obligations: int
    compliance_score: Optional[float]


class RiskSummary(BaseModel):
    contracts_needing_attention: List[RiskItem]