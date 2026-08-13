from fastapi import FastAPI

from app.database.database import test_database_connection

from app.routers.users import router as users_router
from app.routers.authentication import router as auth_router
from app.routers.contract import router as contracts_router
from app.routers.contract_version import router as contract_versions_router
from app.routers.obligation import router as obligations_router
from app.routers.renewal import router as renewals_router
from app.routers.notification import router as notifications_router
from app.routers.report import router as reports_router
from app.routers.audit_log import router as audit_logs_router
from app.routers.activity import router as activities_router


app = FastAPI(
    title="ContractIQ API",
    version="1.0.0"
)


app.include_router(users_router)
app.include_router(auth_router)
app.include_router(contracts_router)
app.include_router(contract_versions_router)
app.include_router(obligations_router)
app.include_router(renewals_router)
app.include_router(notifications_router)
app.include_router(reports_router)
app.include_router(audit_logs_router)
app.include_router(activities_router)


@app.on_event("startup")
def startup_event():
    test_database_connection()


@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend is running successfully."
    }