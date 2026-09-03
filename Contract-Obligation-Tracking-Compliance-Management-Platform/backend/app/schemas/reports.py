from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ============================================================
# Contract Report
# ============================================================

class ContractReportItem(BaseModel):
    contract_id: int
    contract_number: str
    title: str
    category: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class ContractReportResponse(BaseModel):
    total_contracts: int
    active_contracts: int
    draft_contracts: int
    under_review_contracts: int
    approved_contracts: int
    expired_contracts: int
    terminated_contracts: int
    contracts: list[ContractReportItem]


# ============================================================
# Obligation Report
# ============================================================

class ObligationReportItem(BaseModel):
    obligation_id: int
    title: str
    obligation_type: str
    contract_id: int
    contract_number: Optional[str] = None
    due_date: Optional[date] = None
    assigned_to: Optional[int] = None
    assigned_user: Optional[str] = None
    status: str
    completion_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


class ObligationReportResponse(BaseModel):
    total_obligations: int
    pending_obligations: int
    in_progress_obligations: int
    delayed_obligations: int
    overdue_obligations: int
    completed_obligations: int
    obligations: list[ObligationReportItem]


# ============================================================
# Renewal Report
# ============================================================

class RenewalReportItem(BaseModel):
    renewal_id: int
    contract_id: int
    contract_number: Optional[str] = None
    contract_title: Optional[str] = None
    renewal_date: Optional[date] = None
    previous_expiry_date: Optional[date] = None
    new_expiry_date: Optional[date] = None
    status: str
    assigned_to: Optional[int] = None
    assigned_user: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RenewalReportResponse(BaseModel):
    total_renewals: int
    upcoming_renewals: int
    in_progress_renewals: int
    renewed_renewals: int
    expired_renewals: int
    cancelled_renewals: int
    renewals: list[RenewalReportItem]


# ============================================================
# Compliance Report
# ============================================================

class ComplianceReportItem(BaseModel):
    contract_id: int
    contract_number: Optional[str] = None
    compliance_status: str
    compliance_score: float
    total_obligations: int
    completed_obligations: int
    pending_obligations: int
    delayed_obligations: int
    overdue_obligations: int
    risk_level: str
    evaluated_at: Optional[datetime] = None


class ComplianceReportResponse(BaseModel):
    total_contracts: int
    compliant_contracts: int
    pending_contracts: int
    delayed_contracts: int
    non_compliant_contracts: int
    high_risk_contracts: int
    average_compliance_score: float
    compliance_reports: list[ComplianceReportItem]


# ============================================================
# Audit Report
# ============================================================

class AuditReportItem(BaseModel):
    audit_id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    action: str
    table_name: Optional[str] = None
    record_id: Optional[int] = None
    created_at: Optional[datetime] = None


class AuditReportResponse(BaseModel):
    total_audit_logs: int
    audit_logs: list[AuditReportItem]