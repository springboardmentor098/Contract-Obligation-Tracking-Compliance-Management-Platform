from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.all_models import ComplianceStatusEnum, RiskLevelEnum

# 1. Schema for a single compliance database record (History)
class ComplianceRecordResponse(BaseModel):
    id: int
    contract_id: int
    status: ComplianceStatusEnum
    compliance_score: int
    risk_level: RiskLevelEnum
    evaluated_at: datetime
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# 2. Schema for API 1: Get Contract Compliance (Calculated stats)
class ContractComplianceResponse(BaseModel):
    contract_id: int
    compliance_status: ComplianceStatusEnum
    compliance_score: int
    total_obligations: int
    completed_obligations: int
    pending_obligations: int
    overdue_obligations: int
    risk_level: RiskLevelEnum

# 3. Schema for API 3: Get Compliance Summary
class ComplianceSummaryResponse(BaseModel):
    total_contracts: int
    compliant_contracts: int
    pending_contracts: int
    delayed_contracts: int
    non_compliant_contracts: int
    high_risk_contracts: int

# 4. Schema for APIs 4 & 5: Non-Compliant and High-Risk Lists
class ContractRiskResponse(BaseModel):
    contract_id: int
    contract_number: Optional[str] = None 
    compliance_status: Optional[ComplianceStatusEnum] = None
    risk_level: Optional[RiskLevelEnum] = None
    overdue_obligations: int