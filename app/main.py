from fastapi import FastAPI

from app.database.database import test_database_connection
from app.routers.compliance import router as compliance_router
from app.routers.users import router as user_router
from app.routers.auth import router as auth_router
from app.routers.contracts import router as contract_router
from app.routers.obligations import router as obligation_router
from app.models.renewal import Renewal
from app.routers.renewals import router as renewal_router
from app.routers.notifications import router as notification_router
app = FastAPI(
    title="ContractIQ API",
    version="1.0.0"
)


@app.on_event("startup")
def startup_event():
    test_database_connection()


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(contract_router)
app.include_router(obligation_router)
app.include_router(renewal_router)
app.include_router(compliance_router)
app.include_router(notification_router)

@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend is running successfully."
    }