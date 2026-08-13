# app/schemas/report.py

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ReportCreate(BaseModel):
    name: str
    report_type: str
    generated_by: int
    file_path: str | None = None
    format: str


class ReportResponse(BaseModel):
    id: int
    name: str
    report_type: str
    generated_by: int
    file_path: str | None
    format: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
