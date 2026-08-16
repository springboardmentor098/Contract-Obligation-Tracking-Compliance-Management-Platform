from fastapi import FastAPI

from app.database.database import test_database_connection
from app.routers.users import router as user_router
from app.routers.auth import router as auth_router

app = FastAPI(
    title="ContractIQ API",
    version="1.0.0"
)


@app.on_event("startup")
def startup_event():
    test_database_connection()


app.include_router(auth_router)
app.include_router(user_router)


@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend is running successfully."
    }