from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict


# ============================================================
# CONTRACT REPORT
# ============================================================

class ContractReportItem(BaseModel):
    id: int
    contract_number: str
    title: str
    category: str
    start_date: str
    end_date: str
    status: str
    created_by: int
    assigned_to: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ContractSummaryResponse(BaseModel):
    total_contracts: int
    active_contracts: int
    expired_contracts: int
    pending_approval_contracts: int
    contracts_by_status: Dict[str, int]

    # Detailed report records
    contract_records: List[ContractReportItem] = []


# ============================================================
# OBLIGATION REPORT
# ============================================================

class ObligationReportItem(BaseModel):
    id: int
    contract_id: int
    contract_number: Optional[str] = None
    contract_title: Optional[str] = None
    title: str
    description: Optional[str] = None
    obligation_type: str
    due_date: str
    assigned_to: Optional[int] = None
    status: str
    completion_date: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ObligationSummaryResponse(BaseModel):
    total_obligations: int
    pending_obligations: int
    completed_obligations: int
    overdue_obligations: int
    obligations_by_status: Dict[str, int]

    # Detailed report records
    obligation_records: List[ObligationReportItem] = []


# ============================================================
# RENEWAL REPORT
# ============================================================

class RenewalDashboardItem(BaseModel):
    contract_id: int
    contract_number: Optional[str] = None
    contract_title: Optional[str] = None
    expiry_date: Optional[str] = None
    renewal_date: Optional[str] = None
    days_remaining: Optional[int] = None
    status: str


class RenewalSummaryResponse(BaseModel):
    upcoming_renewals: int
    expired_contracts: int
    immediate_attention: int

    renewal_records: List[RenewalDashboardItem] = []


# ============================================================
# COMPLIANCE REPORT
# ============================================================

class ComplianceReportItem(BaseModel):
    contract_id: int
    contract_number: Optional[str] = None
    contract_title: Optional[str] = None

    total_obligations: int
    completed_obligations: int
    pending_obligations: int
    delayed_obligations: int
    overdue_obligations: int

    compliance_score: float
    compliance_status: str
    risk_level: str


class ComplianceSummaryResponse(BaseModel):
    total_contracts: int
    compliant_contracts: int
    pending_contracts: int
    delayed_contracts: int
    non_compliant_contracts: int
    high_risk_contracts: int

    compliance_percentage: float

    # Detailed report records
    compliance_records: List[ComplianceReportItem] = []


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

class DashboardSummaryResponse(BaseModel):
    contracts: ContractSummaryResponse
    obligations: ObligationSummaryResponse
    renewals: RenewalSummaryResponse
    compliance: ComplianceSummaryResponse

    model_config = ConfigDict(from_attributes=True)
