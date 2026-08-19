from fastapi import FastAPI

from app.database.database import test_database_connection
from app.routers.users import router as user_router
from app.routers.auth import router as auth_router
from app.routers.contracts import router as contract_router


app = FastAPI(
    title="ContractIQ API",
    version="1.0.0"
)


@app.on_event("startup")
def startup_event():
    test_database_connection()


@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend is running successfully."
    }


# =========================
# ROUTERS
# =========================

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(contract_router)