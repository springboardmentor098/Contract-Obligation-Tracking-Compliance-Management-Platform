from pydantic import BaseModel


class ComplianceResponse(BaseModel):
    contract_id: int
    compliance_status: str
    compliance_score: int
    total_obligations: int
    completed_obligations: int
    pending_obligations: int
    delayed_obligations: int
    overdue_obligations: int
    risk_level: str


class ComplianceListResponse(BaseModel):
    contract_id: int
    contract_number: str
    compliance_status: str
    compliance_score: int


class ComplianceSummary(BaseModel):
    total_contracts: int
    compliant_contracts: int
    pending_contracts: int
    delayed_contracts: int
    non_compliant_contracts: int
    high_risk_contracts: int


class NonCompliantResponse(BaseModel):
    contract_id: int
    contract_number: str
    compliance_status: str
    overdue_obligations: int


class HighRiskResponse(BaseModel):
    contract_id: int
    contract_number: str
    risk_level: str
    overdue_obligations: int