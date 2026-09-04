from fastapi import FastAPI

from app.database.database import test_database_connection
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router
from app.routers.contracts import router as contracts_router
from app.routers.obligations import router as obligations_router
from app.routers import renewals
from app.routers import compliance
from app.routers import notifications
from fastapi.middleware.cors import CORSMiddleware
from app.routers.reports import router as reports_router

app = FastAPI(
    title="ContractIQ API",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(notifications.router)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(contracts_router)
app.include_router(obligations_router)
app.include_router(renewals.router)
app.include_router(renewals.contract_router)
app.include_router(compliance.router)
app.include_router(reports_router)

@app.on_event("startup")
def startup_event():
    test_database_connection()


@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend is running successfully."
    }