from pydantic import BaseModel
from typing import Dict, List, Any

# 1. Dashboard Summary Schema
class DashboardSummaryResponse(BaseModel):
    contracts: Dict[str, int]
    obligations: Dict[str, int]
    renewals: Dict[str, int]
    compliance: Dict[str, int]

# 2. Risk Analysis Schema
class RiskReportResponse(BaseModel):
    contract_id: int
    contract_number: str
    risk_level: str
    overdue_obligations: int
    compliance_score: int

# 3. Generic Summary Schema (used for Contracts, Obligations, etc.)
class GenericSummaryResponse(BaseModel):
    total: int
    breakdown: Dict[str, int]