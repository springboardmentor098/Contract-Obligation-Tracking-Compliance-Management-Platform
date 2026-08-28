from fastapi import FastAPI

from app.database.database import test_database_connection
from app.api.user_api import router as user_router
from app.api.contract_api import router as contract_router
from app.api.contract_version_api import router as contract_version_router
from app.api.obligation_api import router as obligation_router
from app.api.renewal_api import router as renewal_router
from app.api.notification_api import router as notification_router
from app.api.report_api import router as report_router
from app.api.audit_log_api import router as audit_log_router
from app.api.activity_api import router as activity_router
from app.api.auth_api import router as auth_router
from app.api.compliance_api import router as compliance_router
app = FastAPI(
    title="ContractIQ API",
    version="1.0.0"
)


@app.on_event("startup")
def startup_event():
    test_database_connection()


app.include_router(user_router)
app.include_router(contract_router)
app.include_router(contract_version_router)
app.include_router(obligation_router)
app.include_router(renewal_router)
app.include_router(notification_router)
app.include_router(report_router)
app.include_router(audit_log_router)
app.include_router(activity_router)
app.include_router(auth_router)
app.include_router(compliance_router)
@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend is running successfully."
    }