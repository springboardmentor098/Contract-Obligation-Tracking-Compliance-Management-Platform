# app/schemas/activity.py

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ActivityCreate(BaseModel):
    user_id: int | None = None
    contract_id: int | None = None
    activity_type: str
    description: str


class ActivityResponse(BaseModel):
    id: int
    user_id: int | None
    contract_id: int | None
    activity_type: str
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)