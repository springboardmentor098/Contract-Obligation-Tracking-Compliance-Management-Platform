from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator


CONTRACT_CATEGORIES = {
    "Employment Contract",
    "Vendor Contract",
    "Service Agreement",
    "Lease Agreement",
    "Purchase Agreement",
    "Partnership Agreement",
    "Confidentiality Agreement",
}


CONTRACT_STATUSES = {
    "Draft",
    "Under Review",
    "Approved",
    "Active",
    "Expired",
    "Terminated",
}


class ContractCreate(BaseModel):
    title: str
    contract_number: str
    category: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str):
        if value not in CONTRACT_CATEGORIES:
            raise ValueError(
                f"Invalid contract category. Allowed categories: "
                f"{', '.join(sorted(CONTRACT_CATEGORIES))}"
            )
        return value


class ContractUpdate(BaseModel):
    title: str
    contract_number: str
    category: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str):
        if value not in CONTRACT_CATEGORIES:
            raise ValueError(
                f"Invalid contract category. Allowed categories: "
                f"{', '.join(sorted(CONTRACT_CATEGORIES))}"
            )
        return value


class ContractStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str):
        if value not in CONTRACT_STATUSES:
            raise ValueError(
                f"Invalid contract status. Allowed statuses: "
                f"{', '.join(sorted(CONTRACT_STATUSES))}"
            )
        return value


class ContractAssignment(BaseModel):
    assigned_to: int


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
    assigned_to: int | None
    reviewed_at: datetime | None
    approved_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )