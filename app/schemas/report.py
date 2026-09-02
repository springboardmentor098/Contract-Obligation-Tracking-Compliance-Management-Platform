from pydantic import BaseModel


class ContractReportSummary(BaseModel):
    total_contracts: int
    active_contracts: int
    expired_contracts: int
    contracts_by_category: dict


class ObligationReportSummary(BaseModel):
    total_obligations: int
    completed: int
    pending: int
    delayed: int
    overdue: int


class RenewalReportSummary(BaseModel):
    total_renewals: int
    upcoming: int
    renewed: int
    overdue: int


class RiskReport(BaseModel):
    high_risk_contracts: list
    medium_risk_contracts: list
    low_risk_contracts: list