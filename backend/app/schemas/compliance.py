from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ComplianceResponse(BaseModel):
    id: UUID
    contract_id: UUID

    compliance_score: int = Field(
        ge=0,
        le=100,
    )

    total_obligations: int = Field(
        ge=0,
    )

    completed_obligations: int = Field(
        ge=0,
    )

    pending_obligations: int = Field(
        ge=0,
    )

    overdue_obligations: int = Field(
        ge=0,
    )

    delayed_obligations: int = Field(
        ge=0,
    )

    compliance_status: str
    risk_level: str
    notes: str | None = None
    evaluated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ComplianceSummary(BaseModel):
    total_contracts: int = Field(
        ge=0,
    )

    compliant_contracts: int = Field(
        ge=0,
    )

    non_compliant_contracts: int = Field(
        ge=0,
    )

    high_risk_contracts: int = Field(
        ge=0,
    )

    average_compliance_score: float = Field(
        ge=0,
        le=100,
    )


class ComplianceHistoryResponse(BaseModel):
    contract_id: UUID
    compliance_score: int = Field(
        ge=0,
        le=100,
    )
    compliance_status: str
    risk_level: str
    evaluated_at: datetime

    model_config = ConfigDict(from_attributes=True)