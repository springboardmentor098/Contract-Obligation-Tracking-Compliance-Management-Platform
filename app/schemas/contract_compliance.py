from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ComplianceEvaluationCreate(BaseModel):
    contract_id: int
    notes: Optional[str] = None


class ComplianceEvaluationResponse(BaseModel):
    id: int
    contract_id: int
    status: str
    compliance_score: float
    risk_level: str
    notes: Optional[str] = None
    evaluated_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)