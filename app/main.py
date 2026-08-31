from fastapi import FastAPI

from app.database.database import test_database_connection
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router
from app.api.contracts import router as contracts_router
from app.api.obligations import router as obligations_router
from app.api.obligations import contract_obligations_router
from app.api.renewals import router as renewals_router
from app.api.renewals import contract_renewals_router
from app.api.compliance import router as compliance_router
from app.api.notifications import router as notifications_router


app = FastAPI(
    title="ContractIQ API",
    version="1.0.0"
)


@app.on_event("startup")
def startup_event():
    test_database_connection()


app.include_router(users_router)
app.include_router(auth_router)
app.include_router(contracts_router)
app.include_router(obligations_router)
app.include_router(contract_obligations_router)
app.include_router(renewals_router)
app.include_router(contract_renewals_router)
app.include_router(compliance_router)
app.include_router(notifications_router)


@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend is running successfully."
    }
