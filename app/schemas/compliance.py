from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.compliance import ComplianceStatus, RiskLevel


class ContractComplianceResponse(BaseModel):
    contract_id: int
    contract_number: str
    compliance_status: ComplianceStatus
    compliance_score: float
    total_obligations: int
    completed_obligations: int
    pending_obligations: int
    in_progress_obligations: int
    delayed_obligations: int
    overdue_obligations: int
    risk_level: RiskLevel
    evaluated_at: datetime


class ComplianceListItem(BaseModel):
    contract_id: int
    contract_number: str
    compliance_status: ComplianceStatus
    compliance_score: float


class ComplianceSummary(BaseModel):
    total_contracts: int
    compliant_contracts: int
    pending_contracts: int
    delayed_contracts: int
    non_compliant_contracts: int
    high_risk_contracts: int


class NonCompliantContract(BaseModel):
    contract_id: int
    contract_number: str
    compliance_status: ComplianceStatus
    overdue_obligations: int


class HighRiskContract(BaseModel):
    contract_id: int
    contract_number: str
    risk_level: RiskLevel
    overdue_obligations: int
