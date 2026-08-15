from fastapi import FastAPI

# Database
from app.database.database import test_database_connection

# API routers
from app.api.user_api import router as user_router
from app.api.auth import router as auth_router
from app.api.contract import router as contract_router

# Import all SQLAlchemy models
# This ensures SQLAlchemy knows about all relationships.
from app.models.user import User
from app.models.contract import Contract
from app.models.contract_version import ContractVersion
from app.models.obligation import Obligation
from app.models.renewal import Renewal
from app.models.notification import Notification
from app.models.report import Report
from app.models.audit_log import AuditLog
from app.models.activity import Activity


app = FastAPI(
    title="ContractIQ API",
    version="1.0.0"
)


# -------------------- STARTUP --------------------

@app.on_event("startup")
def startup_event():
    test_database_connection()


# -------------------- ROUTERS --------------------

# User Management APIs
app.include_router(user_router)

# Authentication APIs
app.include_router(auth_router)

# Contract Management APIs
app.include_router(contract_router)


# -------------------- ROOT --------------------

@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend is running successfully."
    }