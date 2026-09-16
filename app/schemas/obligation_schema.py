from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ObligationBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    due_date: date | None = None

    priority: str = Field(
        default="medium",
        min_length=1,
        max_length=50,
    )

    responsible_party: str | None = Field(
        default=None,
        max_length=255,
    )


class ObligationCreate(ObligationBase):
    contract_id: int


class ObligationUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    due_date: date | None = None

    priority: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    responsible_party: str | None = Field(
        default=None,
        max_length=255,
    )


class ObligationStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )


class ObligationRead(ObligationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contract_id: int
    status: str
    created_at: datetime