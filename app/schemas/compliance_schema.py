from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# COMPLIANCE RESPONSE
# ============================================================

class ComplianceResponse(BaseModel):

    contract_id: int

    total_obligations: int

    completed_obligations: int

    pending_obligations: int

    delayed_obligations: int

    overdue_obligations: int

    compliance_score: float = Field(
        ge=0,
        le=100
    )

    compliance_status: str

    risk_level: str

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# COMPLIANCE SUMMARY RESPONSE
# ============================================================

class ComplianceSummaryResponse(BaseModel):

    total_contracts: int

    compliant_contracts: int

    pending_contracts: int

    delayed_contracts: int

    non_compliant_contracts: int

    high_risk_contracts: int

    average_compliance_score: float = Field(
        ge=0,
        le=100
    )

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# COMPLIANCE HISTORY RESPONSE
# ============================================================

class ComplianceHistoryResponse(BaseModel):

    id: int

    contract_id: int

    status: str

    compliance_score: float = Field(
        ge=0,
        le=100
    )

    risk_level: str

    evaluated_at: datetime

    notes: str | None = None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )