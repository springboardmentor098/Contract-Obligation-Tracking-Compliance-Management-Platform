from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import test_database_connection

from app.api.user_api import router as user_router
from app.api.contract_api import router as contract_router
from app.api.obligation_api import router as obligation_router
from app.api.renewal_api import router as renewal_router
from app.api.notification_api import router as notification_router
from app.api.report_api import router as report_router
from app.api.audit_log_api import router as audit_log_router
from app.api.activity_api import router as activity_router
from app.api.auth_api import router as auth_router
from app.api.compliance_api import router as compliance_router
from app.api.dashboard_api import router as dashboard_router

app = FastAPI(
    title="ContractIQ API",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
)

# -----------------------------
# CORS
# -----------------------------
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


from app.core.rbac_seed import ensure_default_rbac_users


@app.on_event("startup")
def startup_event():
    test_database_connection()
    try:
        ensure_default_rbac_users()
    except Exception as e:
        print(f"Warning: RBAC initialization check encountered an error: {e}")


# -----------------------------
# Routers
# -----------------------------
app.include_router(user_router)
app.include_router(contract_router)
app.include_router(obligation_router)
app.include_router(renewal_router)
app.include_router(notification_router)
app.include_router(report_router)
app.include_router(audit_log_router)
app.include_router(activity_router)
app.include_router(auth_router)
app.include_router(compliance_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend is running successfully."
    }