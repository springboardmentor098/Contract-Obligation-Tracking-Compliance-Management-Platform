from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ComplianceResponse(BaseModel):
    contract_id: int
    contract_number: str

    compliance_status: str
    compliance_score: float

    total_obligations: int
    completed_obligations: int
    pending_obligations: int
    delayed_obligations: int
    overdue_obligations: int

    risk_level: str

    evaluated_at: Optional[datetime] = None


class ComplianceSummary(BaseModel):
    total_contracts: int
    compliant_contracts: int
    pending_contracts: int
    delayed_contracts: int
    non_compliant_contracts: int
    high_risk_contracts: int


class ComplianceListResponse(BaseModel):
    contract_id: int
    contract_number: str

    compliance_status: str
    compliance_score: float

    risk_level: str


class NonCompliantResponse(BaseModel):
    contract_id: int
    contract_number: str

    compliance_status: str
    compliance_score: float

    overdue_obligations: int


class HighRiskResponse(BaseModel):
    contract_id: int
    contract_number: str

    risk_level: str
    overdue_obligations: int


class ComplianceHistoryResponse(BaseModel):
    id: int
    contract_id: int

    status: str
    compliance_score: float
    risk_level: str

    notes: Optional[str] = None
    evaluated_at: datetime

    class Config:
        from_attributes = True