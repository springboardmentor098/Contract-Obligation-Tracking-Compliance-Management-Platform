from fastapi import FastAPI

from app.database.database import test_database_connection
from app.api import (
    user_api,
    auth,
    contracts,
    obligations,
    audit_logs,
    contract_versions,
    renewals,
    notifications,
    reports,
    activities,
)
from app.scheduler.scheduler import start_scheduler, stop_scheduler


app = FastAPI(
    title="ContractIQ API",
    version="1.0.0",
)


# ---------------------------------------------------------
# Startup
# ---------------------------------------------------------

@app.on_event("startup")
def startup_event():
    test_database_connection()
    start_scheduler()


# ---------------------------------------------------------
# Shutdown
# ---------------------------------------------------------

@app.on_event("shutdown")
def shutdown_event():
    stop_scheduler()


# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------

app.include_router(user_api.router)
app.include_router(auth.router)
app.include_router(contracts.router)
app.include_router(obligations.router)
app.include_router(audit_logs.router)
app.include_router(contract_versions.router)
app.include_router(renewals.router)
app.include_router(notifications.router)
app.include_router(reports.router)
app.include_router(activities.router)
# ---------------------------------------------------------
# Root
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend is running successfully."
    }