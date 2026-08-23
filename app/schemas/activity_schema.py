from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ActivityCreate(BaseModel):
    user_id: int
    contract_id: int | None = None

    activity_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    description: str | None = None


class ActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    contract_id: int | None
    activity_type: str
    description: str | None
    created_at: datetime
