from datetime import date, datetime

from pydantic import BaseModel


# =========================================================
# CREATE CONTRACT
# =========================================================

class ContractCreate(BaseModel):
    title: str
    contract_number: str
    category: str
    description: str | None = None
    start_date: date
    end_date: date | None = None


# =========================================================
# UPDATE CONTRACT
# =========================================================

class ContractUpdate(BaseModel):
    """
    Schema used to update contract information.

    Status is NOT included here because status changes
    are handled separately through the contract workflow.
    """

    title: str | None = None
    category: str | None = None
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None


# =========================================================
# UPDATE CONTRACT STATUS
# =========================================================

class ContractStatusUpdate(BaseModel):
    """
    Schema used for changing the contract status.
    """

    status: str


# =========================================================
# CONTRACT ASSIGNMENT
# =========================================================

class ContractAssignment(BaseModel):
    """
    Schema used to assign a contract to a responsible user.
    """

    assigned_to: int


# =========================================================
# CONTRACT RESPONSE
# =========================================================

class ContractResponse(BaseModel):
    id: int

    title: str
    contract_number: str
    category: str
    description: str | None

    start_date: date
    end_date: date | None

    # Workflow
    status: str

    # Users
    created_by: int
    assigned_to: int | None

    # Workflow timestamps
    reviewed_at: datetime | None
    approved_at: datetime | None

    # Record timestamps
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True