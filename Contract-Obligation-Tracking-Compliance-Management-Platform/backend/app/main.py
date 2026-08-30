
from fastapi import FastAPI

from app import models

from app.database.database import test_database_connection

from app.api.users import router as user_router
from app.api.auth import router as auth_router
from app.api.contracts import router as contract_router

from app.api.obligations import (
    router as obligation_router,
    contract_obligations_router,
)

# Sprint 10 - Renewal Management
# renewals.py contains a single router
from app.api.renewals import router as renewal_router
from app.api.compliance import router as compliance_router
from app.api.notifications import router as notification_router


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="ContractIQ API",
    version="1.0.0",
)


# ============================================================
# Startup
# ============================================================

@app.on_event("startup")
def startup_event():
    test_database_connection()


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend is running successfully."
    }


# ============================================================
# Include Routers
# ============================================================

# Authentication
app.include_router(auth_router)

# Users
app.include_router(user_router)

# Contracts
app.include_router(contract_router)

# Obligations
app.include_router(obligation_router)

# Contract → Obligations
app.include_router(contract_obligations_router)

# Sprint 10 - Renewals
app.include_router(renewal_router)

# Sprint 11 - Compliance
app.include_router(compliance_router)

# Sprint 12 - Notifications
app.include_router(notification_router)
