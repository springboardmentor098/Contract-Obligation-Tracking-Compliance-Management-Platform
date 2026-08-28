from pydantic import BaseModel


class AuditLogCreate(BaseModel):
    user_id: int
    action: str
    table_name: str
    record_id: int


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    table_name: str
    record_id: int

    class Config:
        from_attributes = True