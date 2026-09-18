from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.security import get_current_user

from app.models.user import User

from app.schemas.dashboard import (
    LegalDashboardResponse,
    ComplianceDashboardResponse,
    AdminDashboardResponse,
)

from app.services.dashboard_service import (
    generate_legal_dashboard,
    generate_compliance_dashboard,
    generate_admin_dashboard,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# ============================================================
# Legal Dashboard
# ============================================================

@router.get(
    "/legal",
    response_model=LegalDashboardResponse,
)
def legal_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return generate_legal_dashboard(db)


# ============================================================
# Compliance Dashboard
# ============================================================

@router.get(
    "/compliance",
    response_model=ComplianceDashboardResponse,
)
def compliance_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return generate_compliance_dashboard(db)


# ============================================================
# Admin Dashboard
# ============================================================

@router.get(
    "/admin",
    response_model=AdminDashboardResponse,
)
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return generate_admin_dashboard(db)