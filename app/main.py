from fastapi import FastAPI

from app.database.database import test_database_connection
from app.routers.users import router as users_router


app = FastAPI(
    title="ContractIQ API",
    version="1.0.0"
)
app.include_router(users_router)

@app.on_event("startup")
def startup_event():
    test_database_connection()


@app.get("/")
def root():
    return {
        "message": "ContractIQ Backend is running successfully."
    }