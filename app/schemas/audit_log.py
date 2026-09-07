# app/schemas/audit_log.py

from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict


class AuditLogCreate(BaseModel):
    user_id: int | None = None
    action: str
    entity_type: str
    entity_id: int | None = None
    old_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None
    ip_address: str | None = None


class AuditLogResponse(BaseModel):
    id: int
    user_id: int | None
    action: str
    entity_type: str
    entity_id: int | None
    old_value: dict[str, Any] | None
    new_value: dict[str, Any] | None
    ip_address: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
