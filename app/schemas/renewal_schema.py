from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class RenewalCreate(BaseModel):
    renewal_date: date
    status: str = Field(
        default="upcoming",
        min_length=1,
        max_length=50,
    )
    renewal_terms: str | None = None


class RenewalUpdate(BaseModel):
    renewal_date: date | None = None
    status: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    renewal_terms: str | None = None


class RenewalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contract_id: int
    renewal_date: date
    status: str
    renewal_terms: str | None
    created_at: datetime
