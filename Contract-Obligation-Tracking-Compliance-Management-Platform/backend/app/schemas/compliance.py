from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ComplianceResponse(BaseModel):
    contract_id: int
    contract_number: str | None = None

    compliance_status: str
    compliance_score: float

    total_obligations: int
    completed_obligations: int
    pending_obligations: int
    delayed_obligations: int
    overdue_obligations: int

    risk_level: str

    evaluated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ComplianceSummaryResponse(BaseModel):
    total_contracts: int
    compliant_contracts: int
    pending_contracts: int
    delayed_contracts: int
    non_compliant_contracts: int
    high_risk_contracts: int


class ComplianceHistoryResponse(BaseModel):
    contract_id: int
    compliance_status: str
    compliance_score: float
    risk_level: str
    evaluated_at: datetime


class RiskInformationResponse(BaseModel):
    contract_id: int
    contract_number: str | None = None
    risk_level: str
    overdue_obligations: int
    delayed_obligations: int
    compliance_score: float