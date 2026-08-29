from pydantic import BaseModel


class ComplianceResponse(BaseModel):
    contract_id: int
    compliance_status: str
    compliance_score: float
    total_obligations: int
    completed_obligations: int
    pending_obligations: int
    overdue_obligations: int
    delayed_obligations: int
    risk_level: str


class ComplianceListResponse(BaseModel):
    contract_id: int
    contract_number: str
    compliance_status: str
    compliance_score: float
    total_obligations: int
    completed_obligations: int
    pending_obligations: int
    overdue_obligations: int
    risk_level: str


class ComplianceSummaryResponse(BaseModel):
    total_contracts: int
    compliant_contracts: int
    pending_contracts: int
    delayed_contracts: int
    non_compliant_contracts: int
    high_risk_contracts: int