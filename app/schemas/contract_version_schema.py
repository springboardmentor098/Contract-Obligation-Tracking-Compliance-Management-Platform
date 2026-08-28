from datetime import datetime

from pydantic import BaseModel


class ContractVersionCreate(BaseModel):
    contract_id: int
    version_number: int
    file_path: str
    uploaded_by: int


class ContractVersionResponse(BaseModel):
    id: int
    contract_id: int
    version_number: int
    file_path: str
    uploaded_by: int

    class Config:
        from_attributes = True