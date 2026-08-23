from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ContractVersionCreate(BaseModel):
    version_number: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    file_name: str | None = Field(
        default=None,
        max_length=255,
    )

    file_path: str | None = Field(
        default=None,
        max_length=500,
    )

    content_hash: str | None = Field(
        default=None,
        max_length=255,
    )

    notes: str | None = None


class ContractVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contract_id: int
    version_number: str
    file_name: str | None
    file_path: str | None
    content_hash: str | None
    notes: str | None
    uploaded_at: datetime
