# app/schemas/contract_version.py

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ContractVersionCreate(BaseModel):
    contract_id: int
    version_number: int
    file_path: str
    change_summary: str | None = None
    created_by: int


class ContractVersionResponse(BaseModel):
    id: int
    contract_id: int
    version_number: int
    file_path: str
    change_summary: str | None
    created_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
