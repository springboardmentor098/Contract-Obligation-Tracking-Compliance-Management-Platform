from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReportCreate(BaseModel):
    user_id: int
    contract_id: int | None = None

    report_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    file_path: str | None = Field(
        default=None,
        max_length=500,
    )


class ReportUpdate(BaseModel):
    report_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    file_path: str | None = Field(
        default=None,
        max_length=500,
    )


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    contract_id: int | None
    report_type: str
    title: str
    description: str | None
    file_path: str | None
    generated_at: datetime
