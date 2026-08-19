from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator


# ============================================================
# OBLIGATION TYPES
# ============================================================

OBLIGATION_TYPES = {
    "Payment Obligation",
    "Delivery Commitment",
    "Reporting Requirement",
    "Renewal Condition",
    "Service Level Agreement",
    "Legal Compliance Requirement",
}


# ============================================================
# OBLIGATION STATUSES
# ============================================================

OBLIGATION_STATUSES = {
    "Pending",
    "In Progress",
    "Completed",
    "Delayed",
    "Overdue",
}


# ============================================================
# CREATE OBLIGATION
# ============================================================

class ObligationCreate(BaseModel):
    contract_id: int
    title: str
    description: str | None = None
    obligation_type: str
    due_date: date
    assigned_to: int

    @field_validator("obligation_type")
    @classmethod
    def validate_obligation_type(cls, value: str):
        if value not in OBLIGATION_TYPES:
            raise ValueError(
                f"Invalid obligation type. Allowed types: "
                f"{', '.join(sorted(OBLIGATION_TYPES))}"
            )
        return value


# ============================================================
# UPDATE OBLIGATION
# ============================================================

class ObligationUpdate(BaseModel):
    title: str
    description: str | None = None
    obligation_type: str
    due_date: date
    assigned_to: int

    @field_validator("obligation_type")
    @classmethod
    def validate_obligation_type(cls, value: str):
        if value not in OBLIGATION_TYPES:
            raise ValueError(
                f"Invalid obligation type. Allowed types: "
                f"{', '.join(sorted(OBLIGATION_TYPES))}"
            )
        return value


# ============================================================
# UPDATE OBLIGATION STATUS
# ============================================================

class ObligationStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str):
        if value not in OBLIGATION_STATUSES:
            raise ValueError(
                f"Invalid obligation status. Allowed statuses: "
                f"{', '.join(sorted(OBLIGATION_STATUSES))}"
            )
        return value


# ============================================================
# COMPLETE OBLIGATION
#
# No completion_date is accepted from client.
# Backend will generate it.
# ============================================================

class ObligationComplete(BaseModel):
    pass


# ============================================================
# OBLIGATION RESPONSE
# ============================================================

class ObligationResponse(BaseModel):
    id: int
    contract_id: int
    title: str
    description: str | None
    obligation_type: str
    due_date: date
    assigned_to: int
    status: str
    priority: str | None
    completion_date: date | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )