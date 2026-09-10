from typing import List, Optional
from pydantic import BaseModel


# -----------------------------
# Dashboard Summary
# -----------------------------

class DashboardSummary(BaseModel):
    total_contracts: int
    active_contracts: int
    total_obligations: int
    pending_obligations: int
    overdue_obligations: int
    upcoming_renewals: int
    high_risk_contracts: int
    compliance_score: float


# -----------------------------
# Contract Statistics
# -----------------------------

class ContractStats(BaseModel):
    total_contracts: int
    active_contracts: int
    draft_contracts: int
    under_review_contracts: int
    approved_contracts: int
    expired_contracts: int
    terminated_contracts: int


# -----------------------------
# Obligation Statistics
# -----------------------------

class ObligationStats(BaseModel):
    total_obligations: int
    completed_obligations: int
    pending_obligations: int
    overdue_obligations: int
    delayed_obligations: int
    completion_rate: float


# -----------------------------
# Renewal Statistics
# -----------------------------

class RenewalStats(BaseModel):
    total_renewals: int
    upcoming_renewals: int
    in_progress_renewals: int
    renewed_renewals: int
    expired_renewals: int
    cancelled_renewals: int


# -----------------------------
# Compliance Statistics
# -----------------------------

class ComplianceStats(BaseModel):
    total_contracts: int
    compliant_contracts: int
    pending_contracts: int
    delayed_contracts: int
    non_compliant_contracts: int
    high_risk_contracts: int
    average_compliance_score: float


# -----------------------------
# Risk Summary
# -----------------------------

class RiskSummary(BaseModel):
    low_risk_contracts: int
    medium_risk_contracts: int
    high_risk_contracts: int
    total_risk_contracts: int


# -----------------------------
# Department Performance
# -----------------------------

class DepartmentPerformance(BaseModel):
    department: str
    total_contracts: int
    total_obligations: int
    completed_obligations: int
    overdue_obligations: int
    compliance_score: float


# -----------------------------
# Export Response
# -----------------------------

class ReportExportResponse(BaseModel):
    filename: str
    content_type: str
    message: str