from typing import Any
from pydantic import BaseModel


class DashboardSummary(BaseModel):
    contracts: dict[str, Any]
    obligations: dict[str, Any]
    renewals: dict[str, Any]
    compliance: dict[str, Any]


class RiskIndicator(BaseModel):
    low: int
    medium: int
    high: int


class RiskSummary(BaseModel):
    risk_indicators: RiskIndicator
    high_risk_contracts: list[dict[str, Any]]


class ReportExportInfo(BaseModel):
    report_type: str
    report_format: str
    filename: str
