from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

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
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True},
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/login",
                    "scopes": {},
                }
            },
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


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