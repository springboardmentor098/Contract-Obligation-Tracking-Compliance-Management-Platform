from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


# ============================================================
# CONTRACT CATEGORIES
# ============================================================

CONTRACT_CATEGORIES = {
    "Employment Contract",
    "Vendor Contract",
    "Service Agreement",
    "Lease Agreement",
    "Purchase Agreement",
    "Partnership Agreement",
    "Confidentiality Agreement",
}


# ============================================================
# CONTRACT STATUS
# ============================================================

CONTRACT_STATUSES = {
    "Draft",
    "Under Review",
    "Approved",
    "Active",
    "Expired",
    "Terminated",
}


# ============================================================
# CREATE CONTRACT
# ============================================================

class ContractCreate(BaseModel):
    title: str
    contract_number: str
    category: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None


# ============================================================
# UPDATE CONTRACT
# ============================================================

class ContractUpdate(BaseModel):
    title: str
    contract_number: str
    category: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = None


# ============================================================
# CONTRACT RESPONSE
# ============================================================

class ContractResponse(BaseModel):
    id: int
    title: str
    contract_number: str
    category: str
    description: str | None
    start_date: date | None
    end_date: date | None
    status: str
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)