from pydantic import BaseModel, Field


class ComplianceResponse(BaseModel):
    contract_id: int

    total_obligations: int
    completed_obligations: int
    pending_obligations: int
    overdue_obligations: int

    compliance_score: float = Field(
        ge=0,
        le=100
    )

    compliance_status: str
    risk_level: str