from fastapi import FastAPI

from app import models

from app.database.database import test_database_connection

from app.api.users import router as user_router
from app.api.auth import router as auth_router
from app.api.contracts import router as contract_router

from app.api.obligations import (
    router as obligation_router,
    contract_obligations_router
)


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="ContractIQ API",
    version="1.0.0"
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

app.include_router(auth_router)

app.include_router(user_router)

app.include_router(contract_router)

app.include_router(obligation_router)

app.include_router(contract_obligations_router)
