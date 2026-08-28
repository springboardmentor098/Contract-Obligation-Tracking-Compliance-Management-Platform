from pydantic import BaseModel


class ComplianceResponse(BaseModel):
    contract_id: int
    contract_title: str
    compliance_score: int
    status: str
    risk_level: str
    total_obligations: int
    completed: int
    pending: int
    overdue: int


class ComplianceSummaryResponse(BaseModel):
    total_contracts: int
    compliant: int
    partially_compliant: int
    non_compliant: int