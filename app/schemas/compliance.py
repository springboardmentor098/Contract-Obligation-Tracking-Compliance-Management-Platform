from datetime import datetime
from typing import Literal

from pydantic import BaseModel


ComplianceStatus = Literal[
    "Compliant",
    "Pending",
    "Delayed",
    "Non-Compliant",
    "High Risk"
]


RiskLevel = Literal[
    "Low",
    "Medium",
    "High"
]


class ComplianceResponse(BaseModel):
    contract_id: int
    compliance_status: ComplianceStatus
    compliance_score: float
    total_obligations: int
    completed_obligations: int
    pending_obligations: int
    overdue_obligations: int
    risk_level: RiskLevel


class ComplianceSummary(BaseModel):
    total_contracts: int
    compliant_contracts: int
    pending_contracts: int
    delayed_contracts: int
    non_compliant_contracts: int
    high_risk_contracts: int


class ComplianceHistory(BaseModel):
    contract_id: int
    compliance_status: ComplianceStatus
    compliance_score: float
    risk_level: RiskLevel
    evaluated_at: datetime


class RiskInformation(BaseModel):
    contract_id: int
    contract_number: str
    risk_level: RiskLevel
    overdue_obligations: int