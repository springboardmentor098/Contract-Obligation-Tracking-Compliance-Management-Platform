from datetime import datetime, date
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, or_, cast, Date
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.activity import Activity
from app.models.user import User
from app.schemas.activity_schema import (
    ActivityCreate,
    ActivityResponse,
    PaginatedActivitiesResponse,
    ActivityFilterOptionsResponse,
)
from app.core.role_checker import RoleChecker
from app.services.activity_service import log_activity


router = APIRouter(
    prefix="/activities",
    tags=["Activities"],
    dependencies=[Depends(RoleChecker(["Admin", "Legal Manager", "Compliance Officer"]))],
)


@router.post(
    "",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED
)
@router.post(
    "/",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False
)
def create_activity(
    activity_data: ActivityCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    activity = log_activity(
        db=db,
        action=activity_data.action or "CUSTOM_ACTIVITY",
        entity_type=activity_data.entity_type or "Activity",
        entity_id=activity_data.entity_id,
        description=activity_data.description or activity_data.activity,
        user_id=activity_data.user_id,
        user_name=activity_data.user_name,
        user_role=activity_data.user_role,
        contract_id=activity_data.contract_id,
        status=activity_data.status or "Success",
        request=request,
        metadata=activity_data.metadata,
    )
    return activity


@router.get(
    "/filter-options",
    response_model=ActivityFilterOptionsResponse
)
def get_activity_filter_options(
    db: Session = Depends(get_db)
):
    """Returns available distinct users, roles, and actions for filter dropdowns."""
    actions_query = db.query(Activity.action).filter(Activity.action.isnot(None)).distinct().all()
    actions = sorted([a[0] for a in actions_query if a[0]])

    roles_query = db.query(Activity.user_role).filter(Activity.user_role.isnot(None)).distinct().all()
    roles = sorted([r[0] for r in roles_query if r[0]])

    users_query = (
        db.query(Activity.user_id, Activity.user_name)
        .filter(Activity.user_name.isnot(None))
        .distinct()
        .all()
    )
    users = [
        {"id": u[0], "name": u[1]}
        for u in users_query
        if u[1]
    ]

    existing_user_ids = {u["id"] for u in users if u["id"] is not None}
    db_users = db.query(User.id, User.full_name, User.role).all()
    for du in db_users:
        if du[0] not in existing_user_ids:
            users.append({"id": du[0], "name": du[1]})

    users.sort(key=lambda x: str(x["name"]))

    return {
        "users": users,
        "roles": roles,
        "actions": actions,
    }


@router.get(
    "",
    response_model=PaginatedActivitiesResponse | list[ActivityResponse]
)
@router.get(
    "/",
    response_model=PaginatedActivitiesResponse | list[ActivityResponse],
    include_in_schema=False
)
def get_activities(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=200, description="Items per page"),
    user_id: int | None = Query(None, description="Filter by User ID"),
    user: str | None = Query(None, description="Filter by User Name or email substring"),
    role: str | None = Query(None, description="Filter by User Role"),
    action: str | None = Query(None, description="Filter by Action type"),
    date_str: str | None = Query(None, alias="date", description="Filter by Date (YYYY-MM-DD)"),
    search: str | None = Query(None, description="Search description, activity, user_name, action, entity_type"),
    contract_id: int | None = Query(None, description="Filter by Contract ID"),
    paginate: bool = Query(True, description="Return paginated object or flat list"),
    db: Session = Depends(get_db)
):
    query = db.query(Activity)

    # Normalize parameters in case called directly as a Python function
    effective_page = page if isinstance(page, int) and page >= 1 else 1
    effective_limit = limit if isinstance(limit, int) and limit >= 1 else 20
    effective_paginate = paginate if isinstance(paginate, bool) else True

    # 1. Contract ID filter
    if isinstance(contract_id, int):
        query = query.filter(Activity.contract_id == contract_id)

    # 2. User filter
    if isinstance(user_id, int):
        query = query.filter(Activity.user_id == user_id)
    elif isinstance(user, str) and user.strip():
        val = user.strip()
        if val.isdigit():
            query = query.filter(or_(Activity.user_id == int(val), Activity.user_name.ilike(f"%{val}%")))
        else:
            query = query.filter(Activity.user_name.ilike(f"%{val}%"))

    # 3. Role filter
    if isinstance(role, str) and role.strip() and role.lower() != "all":
        query = query.filter(func.lower(Activity.user_role) == role.strip().lower())

    # 4. Action filter
    if isinstance(action, str) and action.strip() and action.lower() != "all":
        query = query.filter(func.upper(Activity.action) == action.strip().upper())

    # 5. Date filter
    if isinstance(date_str, str) and date_str.strip():
        try:
            target_date = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
            query = query.filter(cast(Activity.created_at, Date) == target_date)
        except ValueError:
            query = query.filter(cast(Activity.created_at, Date).ilike(f"%{date_str.strip()}%"))

    # 6. Full Search
    if isinstance(search, str) and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Activity.description.ilike(term),
                Activity.activity.ilike(term),
                Activity.user_name.ilike(term),
                Activity.action.ilike(term),
                Activity.entity_type.ilike(term),
                Activity.user_role.ilike(term),
                Activity.status.ilike(term),
                Activity.ip_address.ilike(term),
            )
        )

    # 7. Order by latest first
    query = query.order_by(Activity.created_at.desc(), Activity.id.desc())

    if not effective_paginate:
        return query.all()

    total = query.count()
    items = query.offset((effective_page - 1) * effective_limit).limit(effective_limit).all()
    total_pages = (total + effective_limit - 1) // effective_limit if total > 0 else 1

    return {
        "items": items,
        "total": total,
        "page": effective_page,
        "limit": effective_limit,
        "total_pages": total_pages,
    }


@router.get(
    "/{activity_id}",
    response_model=ActivityResponse
)
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db)
):
    activity = db.query(Activity).filter(
        Activity.id == activity_id
    ).first()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    return activity