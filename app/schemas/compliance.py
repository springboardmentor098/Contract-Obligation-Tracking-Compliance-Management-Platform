from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ContractComplianceResponse(BaseModel):
    contract_id: int
    contract_number: str
    title: str
    compliance_status: str = Field(..., description="Compliance status: Compliant, Pending, Delayed, Non-Compliant, High Risk")
    compliance_score: float = Field(..., description="Compliance percentage (0.0 to 100.0)")
    risk_level: str = Field(..., description="Risk level: Low, Medium, High")
    total_obligations: int
    completed_obligations: int
    pending_obligations: int
    overdue_obligations: int
    delayed_obligations: int
    evaluated_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class ComplianceListItemResponse(BaseModel):
    contract_id: int
    contract_number: str
    title: str
    compliance_status: str
    compliance_score: float
    risk_level: str
    overdue_obligations: int

    class Config:
        from_attributes = True


class ComplianceSummaryResponse(BaseModel):
    total_contracts: int
    compliant_contracts: int
    pending_contracts: int
    delayed_contracts: int
    non_compliant_contracts: int
    high_risk_contracts: int
    average_compliance_score: float


class NonCompliantContractResponse(BaseModel):
    contract_id: int
    contract_number: str
    title: str
    compliance_status: str
    compliance_score: float
    overdue_obligations: int
    risk_level: str


class HighRiskContractResponse(BaseModel):
    contract_id: int
    contract_number: str
    title: str
    risk_level: str
    overdue_obligations: int
    compliance_score: float
    compliance_status: str


class ComplianceHistoryResponse(BaseModel):
    id: int
    contract_id: int
    compliance_status: str
    compliance_score: float
    risk_level: str
    total_obligations: int
    completed_obligations: int
    overdue_obligations: int
    evaluated_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True
