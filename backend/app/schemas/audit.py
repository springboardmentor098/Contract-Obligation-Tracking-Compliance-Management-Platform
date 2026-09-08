from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    entity_type: str
    entity_id: UUID
    action: str
    old_values: dict | None = None
    new_values: dict | None = None
    ip_address: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    data: list[AuditLogResponse]
    total: int