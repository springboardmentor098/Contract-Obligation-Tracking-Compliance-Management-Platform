from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ActivityCreate(BaseModel):
    user_id: int | None = None
    contract_id: int | None = None
    activity: str
    user_name: str | None = None
    user_role: str | None = None
    action: str | None = None
    entity_type: str | None = None
    entity_id: int | None = None
    description: str | None = None
    ip_address: str | None = None
    status: str | None = "Success"
    metadata_json: dict[str, Any] | None = Field(default=None, alias="metadata")


class ActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None = None
    contract_id: int | None = None
    activity: str
    created_at: datetime | None = None
    timestamp: datetime | None = None
    user_name: str | None = None
    user_role: str | None = None
    action: str | None = None
    entity_type: str | None = None
    entity_id: int | None = None
    description: str | None = None
    ip_address: str | None = None
    status: str | None = "Success"
    metadata_json: dict[str, Any] | None = Field(default=None, serialization_alias="metadata")


class PaginatedActivitiesResponse(BaseModel):
    items: list[ActivityResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class ActivityFilterOptionsResponse(BaseModel):
    users: list[dict[str, Any]]
    roles: list[str]
    actions: list[str]