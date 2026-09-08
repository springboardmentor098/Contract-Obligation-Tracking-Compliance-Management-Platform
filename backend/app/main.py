from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import test_database_connection

from app.routers.auth import router as auth_router
from app.routers.users import router as user_router
from app.routers.contracts import router as contracts_router
from app.routers.renewals import router as renewals_router
from app.routers.obligations import router as obligations_router
from app.routers.compliance import router as compliance_router
from app.routers.notifications import router as notifications_router
from app.routers.reports import router as reports_router
from app.routers.audit import router as audit_router


app = FastAPI(
    title="ContractIQ API",
    version="1.0.0",
)


# Allow Angular frontend to communicate with FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    test_database_connection()


# Register API routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(contracts_router)
app.include_router(renewals_router)
app.include_router(obligations_router)
app.include_router(compliance_router)
app.include_router(notifications_router)
app.include_router(reports_router)
app.include_router(audit_router)


@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend is running successfully."
    }