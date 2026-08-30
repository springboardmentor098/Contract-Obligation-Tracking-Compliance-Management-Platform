from fastapi import FastAPI

from app.database.database import test_database_connection

from app.routers.auth import router as auth_router
from app.routers.users import router as user_router
from app.routers.contracts import router as contracts_router
from app.routers.renewals import router as renewals_router
from app.routers.obligations import router as obligations_router
from app.routers.compliance import router as compliance_router
from app.routers.notifications import router as notifications_router


app = FastAPI(
    title="ContractIQ API",
    version="1.0.0",
)


@app.on_event("startup")
def startup_event():
    test_database_connection()


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(contracts_router)
app.include_router(renewals_router)
app.include_router(obligations_router)
app.include_router(compliance_router)
app.include_router(notifications_router)


@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend is running successfully."
    }