from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    action: str
    old_values: Optional[Any] = None
    new_values: Optional[Any] = None
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
